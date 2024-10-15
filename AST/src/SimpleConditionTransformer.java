import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.EnclosedExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class SimpleConditionTransformer extends VoidVisitorAdapter<Void> {
    @Override
    public void visit(BinaryExpr n, Void arg) {
        super.visit(n, arg);

        if (n.getOperator() == BinaryExpr.Operator.GREATER) {
            // 交换并更改操作符为LESS
            Expression left = n.getLeft();
            Expression right = n.getRight();
            n.setLeft(right);
            n.setRight(left);
            n.setOperator(BinaryExpr.Operator.LESS);
        } else if (n.getOperator() == BinaryExpr.Operator.LESS) {
            // 交换并更改操作符为GREATER
            Expression left = n.getLeft();
            Expression right = n.getRight();
            n.setLeft(right);
            n.setRight(left);
            n.setOperator(BinaryExpr.Operator.GREATER);
        } else if (n.getOperator() == BinaryExpr.Operator.AND || n.getOperator() == BinaryExpr.Operator.OR) {
            // 为布尔表达式添加额外的括号
            EnclosedExpr enclosed = new EnclosedExpr(n.clone());
            n.replace(enclosed);
        }
        // 对于等于和不等于操作符，不进行改变
    }
}
