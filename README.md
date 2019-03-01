# refactored-octo-broccoli-kahoot

Refactored Octo Broccoli Kahoot is a simple project I am developing in a class I am enrolled in. It is inspired by the [`Kahoot.it`][kahoot] and it's in the `Python` language.

## Before You Get Started
There are few things you should have installed before we begin. I am using `VSCode` as my text editor, but you can use any text editor you prefer to. I assume you have `Python` installed in your system.

#### Installing `FLASK`

1. Create a folder to start this project, initiate the environtment there by typing this in the `command prompt`
  ```
  python -m venv .\
  ```
  You'll have some folders generated, which are : `Include`,`Lib`,`Projects`,and `Scripts`
2. Go to `Scripts` folder through `command prompt` and activate it by typing
  ```
  activate.bat
  ```
3. Install `FLASK`
  ```
  pip install flask
  ```
  Set the environtment into development mode (optional)
  ```
  set FLASK_ENV=development
  ```
4. Go into `Projects` folder, and create a folder to create your application there. In my case, it's the `kahoot-server` folder. I'm going to create the `app.py` and everything else here
5. To run `FLASK`, go into the folder you want to (where you have set the environtment) and type this in the `command prompt`
  ```
  flask run
  ```
  There are some things you might need to install later, such as `request` to request for data, and you can install it by typing
  ```
  pip install requests
  ```
  
#### Installing `INSOMNIA`
[`INSOMNIA`][insomnia-github] is a cross platform rest client and you can get it [here][insomnia-download]. Installing `INSOMNIA` is quite easy, you just have to follow it and there is no special set up here.

## How To Play
Run `INSOMNIA`, you can make requests as you want it. There are a some types of request, I am using `POST`, `GET`, `DELETE`, and `PUT` request. If you need to send data to the app, you can send some text in `json`-style in the body section. Before sending out request from `INSOMNIA`, make sure your application is running. 
### (to be continued ...)
#### User Registration & Logging In
If a user want to contribute in creating **Quiz** and **Question**, they must create an account first. Later they can log in and contribute. 
#### CRUD a Quiz
#### CRUD a Question
#### Create Game
#### Join Game
#### Leaderboard



[kahoot]: https://kahoot.it
[insomnia-github]: https://github.com/getinsomnia/insomnia
[insomnia-download]: https://insomnia.rest/download/
