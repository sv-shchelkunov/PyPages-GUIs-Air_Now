from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HOST_NAME = "localhost"
SERVER_PORT = 8080

def filter_EmptyStr(arg_Str):
    return len(arg_Str) > 0

class AirNowServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print('command=', self.command)
        print('path=', self.path)

        case=0;
        if ('zipCode' in self.path) and ('distance' in self.path):
            case=1
        if ('startDate' in self.path) and ('endDate' in self.path) and ('BBOX' in self.path):
            case=2

        if case == 0:
            print('Unknown request')
            self.send_response(400)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if case == 1:
            _file = open('req-res-1.txt', 'r')
        if case == 2:
            _file = open('req-res-2.txt', 'r')

        _content = _file.read()
        _result = list(filter(filter_EmptyStr, _content.split('\n')))[1]
        self.wfile.write(bytes(_result, "utf-8"))
        if case == 1:
            print('Date Observed:', json.loads(_result)[0]['DateObserved'])
            print('Latitude:', json.loads(_result)[0]['Latitude'])
            print('Longitude:', json.loads(_result)[0]['Longitude'])

if __name__ == "__main__":
    air_now_server = HTTPServer((HOST_NAME, SERVER_PORT), AirNowServer)
    print(f"Air Now Test Server started at http://{HOST_NAME}:{SERVER_PORT}")

    try:
        air_now_server.serve_forever()
    except KeyboardInterrupt:
        pass

    air_now_server.server_close()
    print("Air Now Test Server is closed")

# screen centering
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
# end of screen centering
