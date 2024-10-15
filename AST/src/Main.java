import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import java.nio.charset.StandardCharsets;

public class Main {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: java Main '<java_code_as_string>' '<perturbation_sequence>'");
            return;
        }
        String javaCode = args[0];
        String[] perturbations = args[1].split(",");

        JavaParser parser = new JavaParser();
        ParseResult<CompilationUnit> parseResult = parser.parse(javaCode);
        if (parseResult.isSuccessful() && parseResult.getResult().isPresent()) {
            CompilationUnit compilationUnit = parseResult.getResult().get();
            PerturbationManager perturbationManager = new PerturbationManager();

            boolean wasModified = false;
            for (String perturbation : perturbations) {
                int perturbationId = Integer.parseInt(perturbation.trim());
                wasModified |= applyPerturbation(perturbationManager, perturbationId, compilationUnit);
            }

            if (wasModified) {
                System.out.println("---START OF CODE---");
                System.out.println(compilationUnit.toString());
                System.out.println("---END OF CODE---");
            } else {
                System.out.println("No modifications were applied.");
            }
        } else {
            System.out.println("Error parsing the code.");
        }
    }

    private static boolean applyPerturbation(PerturbationManager manager, int perturbationId, CompilationUnit compilationUnit) {
        switch (perturbationId) {
            case 1: return manager.applyPerturbation1(compilationUnit);
            case 2: return manager.applyPerturbation2(compilationUnit);
            case 3: return manager.applyPerturbation3(compilationUnit);
            case 4: return manager.applyPerturbation4(compilationUnit);
            case 5: return manager.applyPerturbation5(compilationUnit);
            case 6: return manager.applyPerturbation6(compilationUnit);
            case 7: return manager.applyPerturbation7(compilationUnit);
            case 8: return manager.applyPerturbation8(compilationUnit);
            case 9: return manager.applyPerturbation9(compilationUnit);
            default: System.out.println("Invalid perturbation ID: " + perturbationId); return false;
        }
    }
}
