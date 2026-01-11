import subprocess

passwords = ['', 'password', 'root', 'admin', 'Password123', 'mysql']

for pwd in passwords:
    try:
        cmd = ['mysql', '-u', 'root']
        if pwd:
            cmd.extend(['-p' + pwd])
        cmd.extend(['-e', 'SELECT 1'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f'✓ Success with password: {"(empty)" if not pwd else pwd}')
            break
        else:
            print(f'✗ Failed with password: {"(empty)" if not pwd else pwd}')
    except:
        print(f'✗ Error with password: {"(empty)" if not pwd else pwd}')
