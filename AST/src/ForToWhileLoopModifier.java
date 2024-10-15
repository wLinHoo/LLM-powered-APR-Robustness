import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.expr.BooleanLiteralExpr;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.ForStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.stmt.WhileStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class ForToWhileLoopModifier extends VoidVisitorAdapter<Void> {
    @Override
    public void visit(ForStmt n, Void arg) {
        super.visit(n, arg);

        // 创建while循环的条件，默认为true
        Expression compare = n.getCompare().orElse(new BooleanLiteralExpr(true));

        // 创建while循环的体，包括原for循环体和更新表达式
        BlockStmt body = new BlockStmt();

        // 将原for循环体添加到新的while循环体中
        n.getBody().ifBlockStmt(b -> body.getStatements().addAll(b.getStatements()));
        // 将更新表达式添加到while循环体的末尾
        n.getUpdate().forEach(update -> body.addStatement(new ExpressionStmt(update)));

        // 构造新的while循环
        WhileStmt whileStmt = new WhileStmt(compare, body);

        BlockStmt parentBlock = (BlockStmt) n.getParentNode().orElse(null);
        if (parentBlock == null) {
            return; // 确保父节点是BlockStmt
        }

        // 计算for循环在父BlockStmt中的位置
        int index = parentBlock.getStatements().indexOf(n);

        // 创建一个新的NodeList来存储修改后的语句
        NodeList<Statement> modifiedStatements = new NodeList<>();

        // 添加原for循环之前的所有语句到modifiedStatements
        modifiedStatements.addAll(parentBlock.getStatements().subList(0, index));

        // 如果原for循环有初始化表达式，将其作为独立语句添加
        n.getInitialization().forEach(init -> modifiedStatements.add(new ExpressionStmt(init)));

        // 添加新构造的while循环到modifiedStatements
        modifiedStatements.add(whileStmt);

        // 添加原for循环之后的所有语句到modifiedStatements
        modifiedStatements.addAll(parentBlock.getStatements().subList(index + 1, parentBlock.getStatements().size()));

        // 使用新的语句列表替换原父BlockStmt中的语句
        parentBlock.setStatements(modifiedStatements);
    }
}
