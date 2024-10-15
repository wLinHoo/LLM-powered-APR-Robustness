import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.type.Type;
import com.github.javaparser.ast.expr.NameExpr;

import java.util.LinkedList;
import java.util.List;

public class VariableDeclarationHoister extends VoidVisitorAdapter<Void> {
    @Override
    public void visit(MethodDeclaration n, Void arg) {
        super.visit(n, arg);
        n.getBody().ifPresent(this::hoistVariableDeclarations);
    }

    @Override
    public void visit(ConstructorDeclaration n, Void arg) {
        super.visit(n, arg);
        hoistVariableDeclarations(n.getBody());
    }

    private void hoistVariableDeclarations(BlockStmt body) {
        List<Statement> hoistedDeclarations = new LinkedList<>();
        List<Statement> otherStatements = new LinkedList<>();

        for (Statement stmt : body.getStatements()) {
            if (stmt instanceof ExpressionStmt) {
                ExpressionStmt exprStmt = (ExpressionStmt) stmt;
                if (exprStmt.getExpression() instanceof VariableDeclarationExpr) {
                    VariableDeclarationExpr varDeclExpr = (VariableDeclarationExpr) exprStmt.getExpression();
                    if (varDeclExpr.getVariables().stream().allMatch(v -> !v.getInitializer().isPresent())) {
                        // 如果变量声明没有初始化表达式，则直接提升
                        hoistedDeclarations.add(stmt);
                    } else {
                        // 否则，将声明和赋值分开处理
                        varDeclExpr.getVariables().forEach(v -> {
                            Type type = v.getType();
                            String name = v.getNameAsString();
                            VariableDeclarationExpr decl = new VariableDeclarationExpr(type, name);
                            hoistedDeclarations.add(new ExpressionStmt(decl));
                            v.getInitializer().ifPresent(init -> {
                                AssignExpr assignExpr = new AssignExpr(new NameExpr(name), init, AssignExpr.Operator.ASSIGN);
                                otherStatements.add(new ExpressionStmt(assignExpr));
                            });
                        });
                    }
                    continue;
                }
            }
            otherStatements.add(stmt);
        }

        // 清除原始语句，并首先添加变量声明，然后添加其他语句
        body.getStatements().clear();
        body.getStatements().addAll(hoistedDeclarations);
        body.getStatements().addAll(otherStatements);
    }
}
