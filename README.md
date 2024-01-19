# haloparser

## Install Requirements
Have Python3 and virtualenv installed.
>apt install virtualenv

## Install Steps
```
virtualenv haloparser
cd haloparser
source bin/activate
git clone https://github.com/DanielNagy/haloparser.git
pip install -r requirements.txt
```

## Test BLE function

```
python find.py
```

There should be a Device named HCHLOR. If so, run the following

```
python haloconnect.py
```

This will scan and wait for the Halo to be pairable. Physically on the Halo, go into settings, and enable pairing. The script will then display the Pairing Access code(Write this down), and then pull data from the halo until Control C is pressed to cancel out.

This will NOT save the Access code. So to avoid doing the pairing process everytime you run the haloconnect.py, modify the hayloconnect.py file with your Access Code. 

Find the ACCESS_CODE on line 34, uncomment it, and change the xxxx to include YOUR access code, as captured by the initial pairing. (This is case sensitive)

Then commend out ACCESS_CODE = None on line 35.

Your code should look like this (with xxxx replaced with your access code)
```
    ACCESS_CODE = bytes("xxxx", "utf_8")
    #ACCESS_CODE = None
```

Now when you run `python haloconnect.py` again, it skips the scanning/pairing procedure.
