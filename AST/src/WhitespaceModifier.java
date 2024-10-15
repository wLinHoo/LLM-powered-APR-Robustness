import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.Map;
import java.util.HashMap;

public class WhitespaceModifier {
    public static String removeSpaces(String code) {
        StringBuilder modifiedCode = new StringBuilder();
        String[] lines = code.split("\n");

        Pattern stringLiteralPattern = Pattern.compile("\"[^\"]*\"");
        Pattern operatorPattern = Pattern.compile("\\s*([=+\\-*/])\\s*");

        int placeholderCounter = 0;
        Map<String, String> placeholders = new HashMap<>();

        for (String line : lines) {
            // 使用Matcher来处理字符串字面量
            Matcher matcher = stringLiteralPattern.matcher(line);
            StringBuffer buffer = new StringBuffer();

            while (matcher.find()) {
                String matchedString = matcher.group();
                // 为每个字符串字面量生成一个唯一的占位符
                String placeholder = "%%PLACEHOLDER_" + (placeholderCounter++) + "%%";
                placeholders.put(placeholder, matchedString);
                matcher.appendReplacement(buffer, placeholder);
            }
            matcher.appendTail(buffer);
            String modifiedLine = buffer.toString();

            // 替换等号和加减乘除号两侧的空格
            modifiedLine = operatorPattern.matcher(modifiedLine).replaceAll("$1");

            // 将占位符替换回字符串字面量
            for (Map.Entry<String, String> entry : placeholders.entrySet()) {
                modifiedLine = modifiedLine.replace(entry.getKey(), entry.getValue());
            }

            modifiedCode.append(modifiedLine).append("\n");
        }

        return modifiedCode.toString();
    }
}
