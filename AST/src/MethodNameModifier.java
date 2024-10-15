import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

public class MethodNameModifier extends VoidVisitorAdapter<Void> {
    private Map<String, String> methodNameMapping = new HashMap<>();
    private AtomicInteger counter = new AtomicInteger(1);
    private boolean renameMethods = true;

    @Override
    public void visit(MethodDeclaration n, Void arg) {
        if (renameMethods && !n.getNameAsString().equals("main") && !n.isConstructorDeclaration()) {
            String originalName = n.getNameAsString();
            String modifiedName = originalName + "Method" + counter.getAndIncrement();
            methodNameMapping.put(originalName, modifiedName);
            n.setName(modifiedName);
            System.out.println("Renamed method: " + originalName + " -> " + modifiedName);
        }
        super.visit(n, arg);
    }

    @Override
    public void visit(MethodCallExpr n, Void arg) {
        String methodName = n.getNameAsString();
        if (methodNameMapping.containsKey(methodName)) {
            String newName = methodNameMapping.get(methodName);
            n.setName(newName);
            System.out.println("Updated method call: " + methodName + " -> " + newName);
        }
        super.visit(n, arg);
    }

    public void reset() {
        methodNameMapping = new HashMap<>();
        counter = new AtomicInteger(1);
    }

    public void setRenameMethods(boolean renameMethods) {
        this.renameMethods = renameMethods;
    }
}