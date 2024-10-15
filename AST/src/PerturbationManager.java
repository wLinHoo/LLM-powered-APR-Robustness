import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class PerturbationManager {

    public boolean applyPerturbation1(CompilationUnit compilationUnit) {
        try {
            VariableRenamer variableRenamer = new VariableRenamer();
            variableRenamer.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation2(CompilationUnit compilationUnit) {
        try {
            AddDummyVariableModifier addDummyVariableModifier = new AddDummyVariableModifier();
            addDummyVariableModifier.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation3(CompilationUnit compilationUnit) {
        try {
            AddLineCommentModifier addLineCommentModifier = new AddLineCommentModifier();
            addLineCommentModifier.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation4(CompilationUnit compilationUnit) {
        try {
            AssignExprModifier assignExprModifier = new AssignExprModifier();
            assignExprModifier.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation5(CompilationUnit compilationUnit) {
        try {
            SimpleConditionTransformer simpleConditionTransformer = new SimpleConditionTransformer();
            simpleConditionTransformer.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation6(CompilationUnit compilationUnit) {
        try {
            VariableDeclarationHoister variableDeclarationHoister = new VariableDeclarationHoister();
            variableDeclarationHoister.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation7(CompilationUnit compilationUnit) {
        try {
            ForToWhileLoopModifier forToWhileLoopModifier = new ForToWhileLoopModifier();
            forToWhileLoopModifier.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation8(CompilationUnit compilationUnit) {
        try {
            BinaryExprModifier binaryExprModifier = new BinaryExprModifier();
            binaryExprModifier.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean applyPerturbation9(CompilationUnit compilationUnit) {
        try {
            MethodNameModifier methodNameModifier = new MethodNameModifier();
            // 第一次遍历：重命名方法并填充映射
            methodNameModifier.reset();
            methodNameModifier.setRenameMethods(true);
            methodNameModifier.visit(compilationUnit, null);
            // 第二次遍历：只更新方法调用
            methodNameModifier.setRenameMethods(false);
            methodNameModifier.visit(compilationUnit, null);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
