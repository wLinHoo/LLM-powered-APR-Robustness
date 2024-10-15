import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.util.Optional;

public class AssignExprModifier extends VoidVisitorAdapter<Void> {
    @Override
    public void visit(MethodDeclaration n, Void arg) {
        super.visit(n, arg);

        n.getBody().ifPresent(body -> {
            for (int i = 0; i < body.getStatements().size(); i++) {
                if (body.getStatement(i) instanceof ExpressionStmt) {
                    ExpressionStmt stmt = (ExpressionStmt) body.getStatement(i);
                    if (stmt.getExpression() instanceof AssignExpr) {
                        AssignExpr assignExpr = (AssignExpr) stmt.getExpression();
                        if (assignExpr.getValue() instanceof BinaryExpr) {
                            BinaryExpr binaryExpr = (BinaryExpr) assignExpr.getValue();
                            Expression left = binaryExpr.getLeft();
                            Expression right = binaryExpr.getRight();

                            // 检查赋值表达式的目标是否与二元表达式的一侧相同
                            if (assignExpr.getTarget().equals(right) || assignExpr.getTarget().equals(left)) {
                                // 确定非目标表达式
                                Expression nonTargetExpr = assignExpr.getTarget().equals(left) ? right : left;

                                // 创建新的复合赋值表达式
                                AssignExpr newAssign = new AssignExpr(
                                        assignExpr.getTarget().clone(), nonTargetExpr.clone(), getCorrespondingAssignOperator(binaryExpr.getOperator()));

                                if (newAssign.getOperator() != null) { // 确保有对应的操作符
                                    // 替换原始赋值表达式
                                    stmt.setExpression(newAssign);
                                    System.out.println("Replaced assign expression: " + assignExpr + " with " + newAssign);
                                } else {
                                    System.out.println("No corresponding operator found for: " + binaryExpr.getOperator());
                                }
                            }
                        }
                    }
                }
            }
        });
    }

    private AssignExpr.Operator getCorrespondingAssignOperator(BinaryExpr.Operator binaryOperator) {
        switch (binaryOperator) {
            case PLUS:
                return AssignExpr.Operator.PLUS;
            case MINUS:
                return AssignExpr.Operator.MINUS;
            case MULTIPLY:
                return AssignExpr.Operator.MULTIPLY;
            case DIVIDE:
                return AssignExpr.Operator.DIVIDE;
            // 其他操作符可以根据需要添加
            default:
                return null; // 对于未处理的操作符，返回null
        }
    }
}
