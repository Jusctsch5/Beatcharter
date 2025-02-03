python3 -m venv venv

source venv/bin/activate or venv\Scripts\activate

pip install -r requirements.txt

pytest

# Using the stepchart_parser.py script

python run_stepchart_parser.py "E:\Stepmania\Songs"

python run_stepchart_parser.py "E:\Stepmania\Songs\Mine 4\Sengoku Basara 3 - Naked Arms\basara3.mp3.sm"
python run_stepchart_parser.py "E:\Stepmania\Songs\Anime 1\Bamboo Blade Op\BambooBladeOP.sm"
python run_stepchart_parser.py "E:\Stepmania\Songs\Anime 1\Busou Shoujo Machiavellianism - Shocking Blue\Shocking Blue.sm"

python run_stepchart_parser.py "E:\Stepmania\Songs\Mine 1\Boogiepop and Others\BPop.sm"

# Using the concreator.py script

python run_concreator.py "E:\Stepmania\Songs\Mine 4\Sengoku Basara 3 - Naked Arms\basara3.mp3.sm"
python run_concreator.py "E:\Stepmania\Songs\Anime 1\Bamboo Blade Op\BambooBladeOP.sm"
python run_concreator.py "E:\Stepmania\Songs\Anime 1\Busou Shoujo Machiavellianism - Shocking Blue\Shocking Blue.sm"


python run_concreator.py "E:\Stepmania\Songs\Mine 1" --output .\output\Mine_1
