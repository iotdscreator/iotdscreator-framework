# How to run a server

python3 host_info_manager.py --config ../../config.yaml --log DEBUG

# How to run a client
./host_info_reporter.sh alice 127.0.0.1 3001 atop 10

# You can also run multiple clients
1) Open two terminals

2) [Terminal 1] ./host_info_reporter.sh alice 127.0.0.1 3001 atop 10

3) [Terminal 2] ./host_info_reporter.sh bob 127.0.0.1 3001 atop 10
