import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.UnaryExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.expr.IntegerLiteralExpr;
import com.github.javaparser.ast.expr.EnclosedExpr;

public class BinaryExprModifier extends VoidVisitorAdapter<Void> {
    @Override
    public void visit(BinaryExpr n, Void arg) {
        super.visit(n, arg);

        // 检查是否为字符串连接操作
        if (n.getOperator() == BinaryExpr.Operator.PLUS && (involvesString(n.getLeft()) || involvesString(n.getRight()))) {
            // 如果涉及字符串连接，则不进行扰动
            return;
        }

        switch (n.getOperator()) {
            case PLUS:
            case MULTIPLY:
                // 交换左右操作数
                Expression temp = n.getLeft();
                n.setLeft(n.getRight());
                n.setRight(temp);
                break;
            case MINUS:
                // 改成加一个数的相反数
                n.setOperator(BinaryExpr.Operator.PLUS);
                n.setRight(new UnaryExpr(n.getRight(), UnaryExpr.Operator.MINUS));
                break;
            case DIVIDE:
                // 改成乘上一个数的倒数
                n.setOperator(BinaryExpr.Operator.MULTIPLY);
                EnclosedExpr reciprocal = new EnclosedExpr(new BinaryExpr(new IntegerLiteralExpr(1), n.getRight().clone(), BinaryExpr.Operator.DIVIDE));
                n.setRight(reciprocal);
                break;
            // 其他操作符可以按需添加更多的扰动逻辑
        }
    }

    private boolean involvesString(Expression expr) {
        // 简单检查：如果表达式直接是StringLiteralExpr，则认为涉及字符串
        // 更复杂的情况可能需要类型解析
        return expr.isStringLiteralExpr();
    }
}
