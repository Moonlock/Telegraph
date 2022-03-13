# Telegraph
Send telegrams to and from a Raspberry Pi.

## Setup
### Circuit
The telegraph circuit requires a telegraph key (or button), two buttons, an LED, 3 1kΩ resistors, and a 1 μF capacitor.

GPIO 4 connects to the telegraph key.

![Telegraph key circuit](https://github.com/Moonlock/Telegraph/blob/master/resources/images/telegraphKey.svg)

GPIO 16 connects to the message LED, which indicates whether you have any messages.

An RGB LED is used for status information.  GPIO 13 connects to the red LED and GPIO 19 connects to the green.
The blue LED is not used.

![LED circuit](https://github.com/Moonlock/Telegraph/blob/master/resources/images/LED.svg)

GPIO 20 connects to the 'play message' button, and GPIO 21 to the 'delete message' button.

![Button circuit](https://github.com/Moonlock/Telegraph/blob/master/resources/images/buttons.svg)

GPIO 18 connects to the buzzer.

![Buzzer circuit](https://github.com/Moonlock/Telegraph/blob/master/resources/images/buzzer.svg)

### Configuration
You must run setup.py before running the telegraph for the first time.  This will prompt you to configure a few settings:
 - **WPM playback speed:** Speed of received messages in words per minute.
 - **Local port:** Port the server will listen on.  Default is 8000.
 - **Print received messages:**
 - **Contact mode:** Whether to configure multiple possible contacts, or a single one.  Single Contact
 simplifies sending telegrams.  See below for more details.
 - **Remote IP/hostname, Remote port:** (Single contact mode only) IP address or hostname and port of the destination server.
 - **Play tone when sending:** Plays tone while telegraph key is pressed.
 - **Enable debug info:** Displays (among other things) the duration of each press and release of the telegraph key
in milliseconds.  This may be helpful if you are having trouble getting the correct timing.

#### Multiple Destinations
If Multiple Contacts is used, you will be able to send telegrams to various destinations.  The
configureContacts.py script is used to manage contacts and groups.  Below is an example of
output from the script after a few contacts and a group have been created:

          ~CONTACTS~
    0: Muskrat
        MUSK	172.16.1.63:8000
    1: Moonlock
        MOON	172.16.1.70:8000

          ~GROUPS~
    2: Awesome People
        AWE	Muskrat, Moonlock

    C: Create new contact
    G: Create new group
    D: Delete contact
    Q: Quit

Directly below the name of the contact or group is that destination's call sign.  A call sign is a unique identifier that must
be included in your telegram in order to send it to the configured destination.  Groups consist of multiple contacts, allowing
you to send a telegram to several people simultaneously.  There must already be an entry for for a contact before they can
be added to a group.

If Single Contact is used, you can skip the call sign when sending messages, but will only be able to send to a
single destination.  If you want to change the address or port of the destination, you must stop the server, run setup.py,
then restart the server.

## Usage
### Client/Server
After running setup.py, run start.py to start the client and server.

#### Sending Messages
A telegram must start with the initialisation message `-.-.-` and end with the message `.-.-.`.  If Multiple Contacts is
used, the destination's call sign must immediately follow the init message.  It is also recommended to include your own
call sign so that the recipient(s) can tell who the telegram is from.  This is typically done by sending `DE [call sign]`.
See the example below:

    -.-.-                   (Init message)
    -- ..- ... -.-          (Call sign: MUSK)
    -.. .   -- --- --- -.   (From Moonlock: DE MOON)
    .... . .-.. .-.. ---   .-- --- .-. .-.. -..
                            (Message: HELLO WORLD)
    .-.-.                   (End of message)
   
The init message serves two functions: tells the program that you've started a telegram and sets the time unit of that message.
Time units for the symbols are as follows:
 - dot: 1
 - dash: 3
 - space between symbols in a character: 1
 - space between characters: 3
 - space between words: 7

You can send telegrams at any speed you wish, so long as a dash is always approximately 3 times the length of a dot, and so on.
Once you complete the init message, the time unit will be calculated based on the 9 symbols entered and remain the same for
the rest of the message.  The telegram will send after you finish the end message.  You can then start a new message, and the time unit will be
recalculated based on your next init message.

To cancel a message without sending it, hold down the telegraph key for 3 seconds.  If the time unit for a message is longer
than 300ms the key must be held down for 10 time units, in order to avoid unintentionally cancelling the message.
   
#### Receiving messages
Whenever you receive a telegram, it plays immediately then is added to the end of a queue.  The play button replays the first
message in this queue, and the delete button deletes it.  In order to play a more recent message you must delete all older
messages.

### Running on Computer
A Raspberry Pi is not necessary to run this program; it will also run on a computer, using the keyboard instead of GPIO:
**Telegraph key:** Space bar
**Delete message:** Backspace or Delete
**Play message:** Enter

### Learn Morse code
The learn_morse.py tool was created to help beginners learn Morse code.  It consists of playing random characters for a
configurable amount of time, and giving you a percent correct at the end.  The first time you run it as a new user you will
be prompted to set the initial number of characters used in the test, playback speed in words per minute, and the length of
the test.

It is recommended that you start with only two characters, adding more as you improve.  The program will automatically
increase the amount of characters if you score above 90%.

Another helpful feature when learning Morse code is Farnsworth timing.  A common problem when trying to learn Morse code is
practising at such a low speed (say 5 WPM) that you learn to recognize a character by counting the dots and dashes.
This makes it difficult to increase the speed much beyond 10 WPM, as you no longer have enough time to count individual symbols.
A better way is to learn to recognize the character as a whole, but it can hard to keep up with 15 WPM or upwards when
you are first learning.  Farnsworth timing is a solution to this, whereby you send characters at a faster speed then words
by increasing the time between characters and words.  There are two speed settings; it is recommended that _character speed_
be set to at least 15 WPM, then the _overall speed with Farnsworth timing_ can be reduced initially.

If you would like to make changes to these settings, you can edit `src/learnMorse/users.ini`.
