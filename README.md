
Its a basic tool to test the idea for now.

It has to run as root to intercept keystrokes regardless of app focus.

To run it you first need to create a python venv by running:

`python3 -m venv venv`
Then you activate the venv with:

`source venv/bin/activate`
You then install the requirements with:

`python3 -m pip -r requirements.txt`

Now you can test how it works by running rigctld first if you haven't got one running already:

`./run.sh`

And now you run the actual script as root with sudo:

`sudo venv/bin/python3 ptt.py`

It will ask you which input device is your keyboard, after selecting press some keys and you should see info about it. Then  you can press left CTRL and space (while holding CTRL) to run PTT!
