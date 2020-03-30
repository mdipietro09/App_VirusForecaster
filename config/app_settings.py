
name = "Virus Forecaster"

host = "0.0.0.0"

threaded = False

debug = False

## dev
#port = 5000

## prod
import os
port = int(os.environ.get("PORT", 5000))


