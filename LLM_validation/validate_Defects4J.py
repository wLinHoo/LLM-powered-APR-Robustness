import glob
import json
import time
import javalang
import subprocess
from subprocess import run
import re
import os
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
main_folder = '/home/sdu/Desktop/defects4j/fixed4llmt'
loc_folder = '/home/sdu/Desktop/defects4j/clean_LLM_repair/Defects4j/location'
input_file = "../Defects4j/single_function_repair.json"
def run_d4j_test(source, testmethods, bug_id):
    bugg = False
    compile_fail = False
    timed_out = False
    entire_bugg = False
    error_string = ""

    for t in testmethods:
        cmd = 'defects4j test -w %s/ -t %s' % (('/tmp/' + bug_id), t.strip())
        Returncode = ""
        error_file = open("stderr.txt", "wb")
        child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=error_file, bufsize=-1,
                                 start_new_session=True)
        while_begin = time.time()
        while True:
            Flag = child.poll()
            if Flag == 0:
                Returncode = child.stdout.readlines()
                print(b"".join(Returncode).decode('utf-8'))
                error_file.close()
                break
            elif Flag != 0 and Flag is not None:
                compile_fail = True
                error_file.close()
                with open("stderr.txt", "rb") as f:
                    r = f.readlines()
                for line in r:
                    if re.search(':\serror:\s', line.decode('utf-8')):
                        error_string = line.decode('utf-8')
                        break
                print(error_string)
                break
            elif time.time() - while_begin > 15:
                error_file.close()
                os.killpg(os.getpgid(child.pid), signal.SIGTERM)
                timed_out = True
                break
            else:
                time.sleep(0.01)
        log = Returncode
        if len(log) > 0 and log[-1].decode('utf-8') == "Failing tests: 0\n":
            continue
        else:
            bugg = True
            break

    if not bugg:
        print('So you pass the basic tests, now checking if it passes all the tests, including the previously passing tests.')
        cmd = 'defects4j test -w %s/' % ('/tmp/' + bug_id)
        Returncode = ""
        error_file = open("full_test_stderr.txt", "wb")
        child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=error_file, bufsize=-1,
                                 start_new_session=True)
        while_begin = time.time()
        while True:
            Flag = child.poll()
            if Flag == 0:
                Returncode = child.stdout.readlines()
                print("Full test suite completed.")
                error_file.close()
                break
            elif Flag != 0 and Flag is not None:
                bugg = True
                print("Full test suite failed.")
                error_file.close()
                with open("full_test_stderr.txt", "rb") as f:
                    error_output = f.read().decode('utf-8')
                print("Full test suite errors:\n", error_output)
                break
            elif time.time() - while_begin > 180:
                os.killpg(os.getpgid(child.pid), signal.SIGTERM)
                bugg = True
                print("Full test suite timed out.")
                break
            else:
                time.sleep(0.01)
        log = Returncode
        if len(log) > 0 and log[-1].decode('utf-8') == "Failing tests: 0\n":
            print('All tests passed successfully.')
        else:
            entire_bugg = True
            print("Entire bug found during full test suite.")
            with open("full_test_stdout.txt", "w") as f:
                f.write(b"".join(Returncode).decode('utf-8'))
            with open("full_test_stderr.txt", "rb") as f:
                error_output = f.read().decode('utf-8')
            print("Full test suite stdout:\n", b"".join(Returncode).decode('utf-8'))
            print("Full test suite stderr:\n", error_output)

    return compile_fail, timed_out, bugg, entire_bugg, False

def process_project(llm_folder, project_folder, bug_dict, loc_folder):
    llm_name = os.path.basename(llm_folder)
    project_id = os.path.basename(project_folder)
    plausible = 0
    total = 0
    for file in sorted(glob.glob(project_folder + '/*.java')):
        file_name = os.path.basename(file)
        bug_id_parts = file_name.split('-')
        bug_id = '-'.join(bug_id_parts[:2])
        project, bug = bug_id.split('-')

        if bug_id not in bug_dict:
            print(f"Skipping {bug_id}, not found in bug dictionary.")
            continue

        start = bug_dict[bug_id]['start']
        end = bug_dict[bug_id]['end']
        tmp_bug_id = "test_" + bug_id

        print(f"Processing {file}, bug ID {bug_id}")

        run(f'rm -rf /tmp/{tmp_bug_id}', shell=True)
        run(f"defects4j checkout -p {project} -v {bug + 'b'} -w /tmp/{tmp_bug_id}", shell=True)
        testmethods = subprocess.check_output(f'defects4j export -w /tmp/{tmp_bug_id} -p tests.trigger', shell=True).decode().splitlines()
        source_dir = subprocess.check_output(f"defects4j export -p dir.src.classes -w /tmp/{tmp_bug_id}", shell=True).decode().strip()

        loc_file_path = os.path.join(loc_folder, f"{bug_id}.buggy.lines")
        try:
            with open(loc_file_path, "r") as loc_file:
                loc = loc_file.read().splitlines()[0].split("#")[0]
        except FileNotFoundError:
            print(f"Location file for {bug_id} not found.")
            continue

        source_file_path = f"/tmp/{tmp_bug_id}/{source_dir}/{loc}"
        print(source_file_path)
        try:
            with open(source_file_path, 'r') as f:
                source = f.readlines()
            with open(file, 'r') as f:
                patch = f.readlines()

            new_source = source[:start - 1] + patch + source[end:]
            with open(source_file_path, 'w') as f:
                f.writelines(new_source)

            compile_fail, timed_out, bugg, entire_bugg, syntax_error = run_d4j_test(new_source, testmethods, tmp_bug_id)
            result_dir = os.path.join('fixresult', llm_name)
            os.makedirs(result_dir, exist_ok=True)
            if not compile_fail and not timed_out and not bugg and not entire_bugg and not syntax_error:
                plausible += 1
                message = f"{bug_id} has valid patch: {file}"
                print(f"{bug_id} has valid patch: {file}")
                with open(os.path.join(result_dir, f'valid-{llm_name}-{project_id}.txt'), 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
            else:
                message = f"{bug_id} has invalid patch: {file}"
                print(f"{bug_id} has invalid patch: {file}")
                with open(os.path.join(result_dir, f'invalid-{llm_name}-{project_id}.txt'), 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
        except Exception as e:
            print(f"Error processing {bug_id}: {e}")

        total += 1

    print(f"{plausible}/{total} patches are plausible for project {project_id}.")

def validate_all_patches(main_folder, loc_folder):
    with open(input_file, "r") as f:
        bug_dict = json.load(f)

    tasks = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        for llm_folder in glob.glob(main_folder + '/*'):
            for project_folder in glob.glob(llm_folder + '/*'):
                tasks.append(executor.submit(process_project, llm_folder, project_folder, bug_dict, loc_folder))

        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                print(f"Error in processing: {e}")


validate_all_patches(main_folder, loc_folder)
