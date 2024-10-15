import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.stmt.ForStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;

public class VariableRenamer extends VoidVisitorAdapter<Void> {
    private final Map<String, String> variableNameMapping = new HashMap<>();
    private final AtomicInteger counter = new AtomicInteger(1);

    @Override
    public void visit(VariableDeclarator n, Void arg) {
        Optional<ForStmt> forStmt = n.findAncestor(ForStmt.class);
        boolean isForLoopControl = forStmt.isPresent() &&
                (forStmt.get().getInitialization().stream().anyMatch(init -> init instanceof VariableDeclarationExpr &&
                        ((VariableDeclarationExpr) init).getVariables().contains(n)) ||
                 forStmt.get().getUpdate().stream().anyMatch(update -> update.toString().contains(n.getNameAsString())));

        if (!isForLoopControl) {
            String originalName = n.getNameAsString();
            String newName = originalName + "_var" + counter.getAndIncrement();
            variableNameMapping.put(originalName, newName);
            n.setName(newName);
            System.out.println("Renamed variable: " + originalName + " -> " + newName);
        } else {
            System.out.println("Skipping loop control variable: " + n.getNameAsString());
        }
        super.visit(n, arg);
    }

    @Override
    public void visit(NameExpr n, Void arg) {
        String originalName = n.getNameAsString();
        Optional<ForStmt> forStmt = n.findAncestor(ForStmt.class);
        boolean isForLoopControl = forStmt.isPresent() &&
                (forStmt.get().getInitialization().stream().anyMatch(init -> init.toString().contains(originalName)) ||
                 forStmt.get().getUpdate().stream().anyMatch(update -> update.toString().contains(originalName)));

        if (isForLoopControl) {
            System.out.println("Skipping loop control variable usage: " + originalName);
        } else if (variableNameMapping.containsKey(originalName)) {
            String newName = variableNameMapping.get(originalName);
            n.setName(newName);
            System.out.println("Updated variable usage: " + originalName + " -> " + newName);
        }
        super.visit(n, arg);
    }
}