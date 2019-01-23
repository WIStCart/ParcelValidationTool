How to Compile the .jsx code into .js (There are other routes to achieving this but the following is what we have done so-far)
1) main.js contains the .jsx code. It is not used by the final page but instead for React.js development (validation_babel.html includes it).
	a) The reason that we need to compile the code is that the application will not work for some browsers if left uncompiled and executing the application from a local directory without a localhost. The .jsx code will work just fine on a server or localost (but the validation tool needs to open it from a random local directory) 
2) main_compiled.js contains the final code that will ship with the validation tool (validation.html includes it).
3) In order to make a change to the application, make the change in main.js and translate or "compile" the code using Babel. Heres how to do that:
	a) Open https://babeljs.io/ and go to the "Try it out" section (https://babeljs.io/repl). Default configurations should be fine for our purposes. It may be beneficial to use incognito mode (I was having trouble with its stateful url which seemed to cause caching old version of the .jsx)
	b) Paste the entire content of main.js into the window to the left.
	c) Automatically, the pure .js will populate the right window. Copy it and paste it into main_compiled.js (replacing any code that previously existed here)
	d) Thats it, the validation.html will already include main_compiled.js so it should work right away