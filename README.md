# Login Example v2.1.0 (5 July 2026)

This sample app demonstrates a simple login system that allows users to
register, log in, and view pages specific to their user role. Those pages don't
really do anything: it's just a simplified example to share some basic tools
and techniques you might need when building a real-world login system.

There are three user roles in this system:
- **Customer**
- **Staff**
- **Admin**

Anyone who registers via the app will be a **Customer**. The only way to create
**Staff** or **Admin** accounts in this simple app is to insert them directly
into the database. Hey, we didn't say this app was complete!

## Getting this Example Running

To run the example yourself, you'll need to:

1. Open the project in Visual Studio Code.
2. Create yourself a virtual environment.
3. Install all of the packages listed in [requirements.txt](requirements.txt)
   (Visual Studio will offer to do this for you during step 2).
4. Create a **loginexample** database in PostgreSQL.

   For example, from the Windows command line:\
   ```createdb -U postgres loginexample```
5. Run the [Database Creation Script](create_database.sql) on your
   **loginexample** database to create the necessary ***users*** table.

   For example, from the Windows command line:\
   ```psql -U postgres -d loginexample -f create_database.sql``` 
6. Use the [Database Population Script](populate_database.sql) to populate
   the **loginexample** ***users*** table with example users.

   For example, from the Windows command line:\
   ```psql -U postgres -d loginexample -f populate_database.sql``` 
7. Modify [connect.py](loginapp/connect.py) with the connection details for
   your local database server.
8. Run [The Python/Flask application](run.py).

At that point, you should be able to register yourself a new **customer**
account or log in using one of the **customer**, **staff**, or **admin**
accounts listed in the [Database Population Script](populate_database.sql).

Enjoy!

## Database Scripts

While we're talking about the database, you should take a look at:
- [PostgreSQL script to create the necessary table](create_database.sql)
- [PostgreSQL script to populate the database with users](populate_database.sql)
- [Python script to create password hashes](password_hash_generator.py)

What's that third one? Well, for that we need to talk about...

## Passwords

One of the key things about this login system is that it doesn't actually store
users' passwords in the database. That may lead you to ask...

### Why not store passwords?
People tend to re-use passwords across multiple websites, no matter how much
security experts might tell them not to. That means if someone gets access to
your database, containing a whole lot of users' passwords and other details
like names or email addresses, they can use those passwords to compromise
your users' accounts with other services (like their email, or bank account).

### How do you handle registration and login without storing passwords?

Easy! Well, sort of. It goes like this:

1. When the user first gives us a password during registration, we pass it
   through a cryptographic "hash" function: a one-way mathematical operation
   that transforms the original password into its corresponding "hash value"
   or "hash". The same password always results in the same hash.
   
2. We throw away the original password, and just keep the hash.
   
3. The hash value is useless to an attacker: because the hash-function is
   one-way, anyone who steals our database of user accounts can't work out
   what the users' passwords are. Well, okay, there are clever ways around
   that. Look up "rainbow tables" if you're interested. Read Cory Doctorow's
   "Knights of the Rainbow Table" if you're *really* interested. But it takes
   a whole lot more time and computing power for an attacker to get a user's
   password back from its hash than it does to just read the plain password
   straight out of your database.

4. When a user tries to log in, we take the password they supplied us, run it
   through the exact same hash function, and then compare the hash to the one
   we have on file. Because the same password will always produce the same
   hash, if the two hashes match then the passwords must match! Again, kinda.
   It's possible, though very unlikely, that two passwords may produce the
   same hash value. In that case, you'd be able to log in using either
   password. These kinds of "hash collisions" are extremely rare, though. Rare
   enough that we won't worry about that here.

So, in short:
1. The user gives us a password.
2. We put that password though a one-way hashing algorithm to get its "hash".
3. We store the hash, **not** the password.
4. During login, we put the supplied password through the same algorithm.
5. If the hash of the supplied password matches the hash of the user's original
   password that we stored in step 3, then we know the user has supplied the
   correct password... without having to know their password at all.

Cool, huh?

### Salting Passwords

Remember how we mentioned that it's technically possible for an attacker to
work out a user's original password from its hash, just expensive? Well, it's
actually not expensive at all if you just pre-calculate one of those "rainbow
tables": essentially a giant table mapping hash values back to passwords. It
takes time to generate something like that, and the tables are absolutely huge,
but storage is pretty cheap these days and you only have to generate the table
once per hash algorithm. Once someone has a rainbow table for a particular
algorithm, translating hashes back to passwords is just a simple lookup.

The contemporary solution to this is to add a "salt" to each password before
you hash it. The salt is just some random string. It doesn't have to be secret,
necessarily, just specific to your app (which we used to do in older versions
of this example project) or, ideally, specific to each password (which we do in
this current version). Adding a salt to your passwords totally breaks the whole
"rainbow table" approach: an attacker can't just use an off-the-shelf table
any more. With our old approach, one salt for the whole app, an attacker needs
to generate a rainbow table specific to *our application's salt*. When you're
using per-password salts, like we are here, an attacker would have to generate
one of those giant tables to break *each individual password* in our database.

Quantum computing will probably break all this, in the not-too-distant future,
but for now this approach provides a reasonable means of protecting users'
passwords from disclosure if an attacker gains access to our database.

### How exactly do we do all this?

With the [Flask-Bcrypt library](https://flask-bcrypt.readthedocs.io/en/1.0.1/)
(which is really just a Flask-specific wrapper for the bcrypt library) and a
couple lines of code.

If you take a look at the [database creation script](create_database.sql),
you'll see that instead of a "password" field to store the password, we have a
"password_hash" field that stores a string of text. Check out the
[populate database script](populate_database.sql), and you'll see these aren't
human-readable passwords.

Flask-Bcrypt uses the [bcrypt algorithm](https://en.wikipedia.org/wiki/Bcrypt)
(as you may have guessed from the name). Bcrypt password hashes bundle together
a bcrypt version number, the password hash itself, and the salt value used to
generate it. Together, depending on which version of the algorithm you're
using, this is a string of either 59 or 60 bytes (always 60 bytes in the
current version).

If this sounds terrifyingly complicated, don't worry. Take a look at the
[Hash generator Python script](password_hash_generator.py) for an example of
how to create the hashes (literally one line of code) and check a password
against a hash (again, one line of code).

If we were using the bcrypt library directly, or another option such as
[Flask-Hashing](https://flask-hashing.readthedocs.io/en/latest/) (used in older
versions of this example) then we'd need to handle the "salting" process
ourselves. However, the Flask-Bcrypt library does this for us. We only have to
call the `generate_password_hash(password)` function to generate a hash for a
new `password` (e.g. when a user signs up or changes their password). That
function generates a new salt value then uses it to hash the password in a
single step.

Once we've generated a password hash and stored it in our database, we can then
call the `check_password_hash(pw_hash, password)` function to check a whether a
`password` supplied during login matches the `pw_hash` stored in our database
for that particular user account.

### Storing password hashes in PostgreSQL

The string of bytes making up a bcrypt hash are all in the "printable
character" range, so can be displayed a text string. In a PostgreSQL database
you could store these as:
- `CHAR(60)` - Exactly 60 characters
- `VARCHAR(60)` - Up to 60 characters
- `TEXT` - Any number of characters

We use latter format (`TEXT`) in this example because there's no performance
advantage to using `CHAR` or `VARCHAR` in PostgreSQL. These are stored the same
as `TEXT` "under the hood"; the only difference is that they're limited to a
set or maximum length.

We've chosen to use `VARCHAR` columns for our username and email address fields
to enforce "business rules" around their lengths: we want to ensure the system
cannot accept user names beyond our chosen maximum of 20 characters, or email
addresses that are unrealistically long. However, we don't have any business
rules around the length of a hash: using `TEXT` allows us to adapt to future
changes in bcrypt, or a new hashing algorithm altogether, without modifying the
database.