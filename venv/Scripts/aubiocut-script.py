#!E:\Projects\Beatcharter\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'aubio==0.4.9','console_scripts','aubiocut'
__requires__ = 'aubio==0.4.9'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('aubio==0.4.9', 'console_scripts', 'aubiocut')()
    )
