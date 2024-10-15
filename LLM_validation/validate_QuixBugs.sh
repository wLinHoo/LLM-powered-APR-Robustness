#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 定义目录
LLM_DIR="/home/sdu/Desktop/defects4j/clean_LLM_repair/70b"
JAVA_PROGRAMS_DIR="$SCRIPT_DIR/java_programs"
JAVA_PROGRAMS_COPY_DIR="/home/sdu/Desktop/defects4j/clean_LLM_repair/java_programs_copy"

# 定义测试结果文件
RESULT_FILE="$SCRIPT_DIR/test_results_70b.txt"
FAILURE_FILE="$SCRIPT_DIR/test_failures_m.txt"

# 清空结果文件
echo "" > "$RESULT_FILE"
echo "" > "$FAILURE_FILE"

# 计数器
count=0

# 测试的文件数量限制
MAX_FILES=40

# 创建一个函数来复制文件和运行测试
copy_and_test() {
    local src_file=$1
    local base_name=$(basename "$src_file" .java)
    local dest_file="$JAVA_PROGRAMS_DIR/$base_name.java"
    local test_name="java_testcases.junit.${base_name}_TEST"

    # 备份现有文件
    if [ -e "$dest_file" ]; then
        mv "$dest_file" "$JAVA_PROGRAMS_COPY_DIR/$base_name.java.bak"
        echo "Backed up original $dest_file to $JAVA_PROGRAMS_COPY_DIR/$base_name.java.bak"
    fi

    # 复制文件到java_programs
    cp "$src_file" "$dest_file"
    echo "Copied $src_file to $dest_file"

    # 运行测试
    /opt/gradle/latest/bin/gradle test --tests "$test_name" >> gradle_output.txt 2>&1

    if grep -q "BUILD SUCCESSFUL" gradle_output.txt; then
        echo "$test_name Successful" >> "$RESULT_FILE"
    else
        echo "$test_name Failed" >> "$RESULT_FILE"
        echo "$test_name Failed with errors:" >> "$FAILURE_FILE"
        cat gradle_output.txt >> "$FAILURE_FILE"
        echo -e "\n\n" >> "$FAILURE_FILE"
    fi

    # 删除临时输出文件
    rm gradle_output.txt

    # 恢复java_programs中的原始文件
    if [ -e "$JAVA_PROGRAMS_COPY_DIR/$base_name.java.bak" ]; then
        mv "$JAVA_PROGRAMS_COPY_DIR/$base_name.java.bak" "$dest_file"
        echo "Restored original $base_name.java from backup"
    else
        rm "$dest_file"
        echo "Removed $dest_file as no backup was found"
    fi
}

# 遍历llm目录中的所有文件
for FILE in "$LLM_DIR"/*.java; do
    if [ $count -ge $MAX_FILES ]; then
        break
    fi

    # 检查文件是否存在
    if [ -e "$FILE" ]; then
        # 复制并测试文件
        copy_and_test "$FILE"
        
        # 增加计数器
        count=$((count + 1))
    fi
done

echo "All tests completed. Results are saved in $RESULT_FILE. Failures are saved in $FAILURE_FILE."
