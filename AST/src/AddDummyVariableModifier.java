import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.type.PrimitiveType;
import com.github.javaparser.ast.expr.IntegerLiteralExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class AddDummyVariableModifier extends VoidVisitorAdapter<Void> {
    private int variableCounter = 1; // 初始值设为1，用于变量名的递增

    @Override
    public void visit(MethodDeclaration n, Void arg) {
        if (n.getBody().isPresent()) {
            BlockStmt body = n.getBody().get();

            // 使用变量计数器创建变量名，然后递增计数器
            String varName = "dummyVar" + variableCounter++;
            VariableDeclarator variableDeclarator = new VariableDeclarator(
                PrimitiveType.intType(), varName, new IntegerLiteralExpr("0"));
            VariableDeclarationExpr dummyVarExpr = new VariableDeclarationExpr(variableDeclarator);

            ExpressionStmt dummyVarStmt = new ExpressionStmt(dummyVarExpr);

            // 随机选择一个插入点
            int insertIndex = (int) (Math.random() * (body.getStatements().size() + 1));

            // 在随机位置插入新的局部变量声明
            body.getStatements().add(insertIndex, dummyVarStmt);
        }
        super.visit(n, arg);
    }
}
