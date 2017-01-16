IF EXIST dist RMDIR dist /S /Q
MKDIR dist
MKDIR dist\dric
MKDIR dist\plugins
MKDIR dist\dricgcss_index\dist
XCOPY dric dist\dric
XCOPY plugins dist\plugins /E
XCOPY dricgcss_index\dist dist\dricgcss_index\dist /E
COPY logging.yml dist
COPY main.py dist
COPY README.md dist
COPY requirements.txt dist