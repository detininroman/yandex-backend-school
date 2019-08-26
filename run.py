from service import app
from service import host
from service import port

app.run(host=host, port=port, debug=True, threaded=True)
