from flask import Blueprint
from pathlib import Path

router = Blueprint('router',__name__)
# define file address
baseLocation = Path(__file__).absolute().parent.parent # naik ke folder src

# import semua route yang ada ke sini
from .userRoute import *
from .quizRoute import *
from .questionRoute import *
from .gameRoute import *
from .errorRoute import *
