import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.comments.LineComment;

import java.util.Random;
import java.util.UUID;

public class AddLineCommentModifier extends VoidVisitorAdapter<Void> {
    private final Random random = new Random();

    @Override
    public void visit(MethodDeclaration n, Void arg) {
        super.visit(n, arg);

        if (n.getBody().isPresent()) {
            BlockStmt body = n.getBody().get();

            // 创建一个唯一的注释内容
            String commentContent = "This method was modified - " + UUID.randomUUID().toString();

            // 创建一个行注释节点
            LineComment lineComment = new LineComment(commentContent);

            // 随机选择一个插入点
            int insertIndex = random.nextInt(body.getStatements().size());

            // 在随机位置的语句上添加注释
            body.getStatements().get(insertIndex).setComment(lineComment);
        }
    }
}
