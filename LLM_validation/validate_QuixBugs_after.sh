#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 定义目录
LLM_DIR="/home/sdu/Desktop/defects4j/clean_LLM_repair/fixedquix/8b"
JAVA_PROGRAMS_DIR="/home/sdu/Desktop/defects4j/clean_LLM_repair/QuixBugs-master/java_programs"
JAVA_PROGRAMS_COPY_DIR="/home/sdu/Desktop/defects4j/clean_LLM_repair/QuixBugs-mastercopy/java_programs"
RESULT_FILE="$SCRIPT_DIR/8b_results.txt"
ERROR_FILE="$SCRIPT_DIR/test_errors.txt"

# 清空结果文件
echo "" > "$RESULT_FILE"
echo "" > "$ERROR_FILE"

# 创建一个函数来复制文件内容并运行测试
copy_and_test_content() {
    local src_file=$1
    local src_base_name=$2
    local version_name=$3
    local test_name="java_testcases.junit.${src_base_name}_TEST"

    # 恢复原有文件夹
    rsync -a --delete "$JAVA_PROGRAMS_COPY_DIR/" "$JAVA_PROGRAMS_DIR"
    echo "Restored JAVA_PROGRAMS_DIR from backup before testing"

    # 读取源文件内容
    local content=$(cat "$src_file")

    # 构建目标文件的完整路径
    local dest_file="$JAVA_PROGRAMS_DIR/$src_base_name.java"

    # 将内容写入目标文件
    echo "$content" > "$dest_file"
    echo "Copied content of $src_file to $dest_file"

    # 运行测试
    /opt/gradle/latest/bin/gradle test --tests "$test_name" > gradle_output.txt 2>&1

    if grep -q "BUILD SUCCESSFUL" gradle_output.txt; then
        echo "$version_name Successful" >> "$RESULT_FILE"
    else
        echo "$version_name Failed" >> "$RESULT_FILE"
        echo "Error details for $version_name:" >> "$ERROR_FILE"
        cat gradle_output.txt >> "$ERROR_FILE"
        echo "" >> "$ERROR_FILE"
    fi

    # 删除临时输出文件
    rm gradle_output.txt
}

# 遍历llm目录中的所有子文件夹
for PROJECT_DIR in "$LLM_DIR"/*/; do
    PROJECT_NAME=$(basename "$PROJECT_DIR")

    # 遍历子文件夹中的所有文件
    for FILE in "$PROJECT_DIR"/*.java; do
        if [ -e "$FILE" ]; then
            # 复制并测试文件内容
            copy_and_test_content "$FILE" "$PROJECT_NAME" "$(basename "$FILE")"
        fi
    done
done

echo "All tests completed. Results are saved in $RESULT_FILE. Error details are saved in $ERROR_FILE."
