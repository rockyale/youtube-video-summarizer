import subprocess
import shutil
import os

def build_lambda(source_dir, output_dir):
    # Create a temporary directory for building
    build_dir = os.path.join(output_dir, 'build')
    os.makedirs(build_dir, exist_ok=True)

    # Copy all files from source to build directory
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(build_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks=False, ignore=None)
        else:
            shutil.copy2(s, d)

    # Install requirements
    requirements_file = os.path.join(source_dir, 'requirements.txt')
    if os.path.exists(requirements_file):
        subprocess.check_call([
            'pip',
            'install',
            '-r',
            requirements_file,
            '--target',
            build_dir,
            '--upgrade'
        ])

    return build_dir

if __name__ == '__main__':
    build_lambda('lambda/summarizer', 'lambda_build')