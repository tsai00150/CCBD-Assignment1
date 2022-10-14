@ECHO OFF
for /r %%i in (*.json) do (
    aws dynamodb batch-write-item --request-items file://%%i
)
PAUSE