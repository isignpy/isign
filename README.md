
[![CircleCI](https://circleci.com/gh/isignpy/isign/tree/master.svg?style=svg)](https://circleci.com/gh/isignpy/isign/tree/master)

isign
=====

A tool and library to re-sign iOS applications, without proprietary Apple software.

For example, an iOS app in development would probably only run on the developer's iPhone.
`isign` can alter the app so that it can run on another developer's iPhone.

Apple tools already exist to do this. But with `isign`, now you can do this on operating
systems like Linux.


Table of contents
-----------------

-   [Installing](#Installing)
-   [How to get started](#How-to-get-started)
-   [How to use isign](#How-to-use-isign)
-   [isign command line arguments](#isign-command-line-arguments)
-   [Contributing](#Contributing)
-   [More documentation](#More-documentation)
-   [Authors](#Authors)

Installing
----------

### Linux

The latest version of `isign` can be installed via [PyPi](https://pypi.python.org/pypi/isign/):

``` {.sourceCode .}
$ pip install isign
```

### Mac OS X

On Mac OS X, there are a lot of prerequisites, so the `pip` method probably won't work.
The easiest method is to use `git` to clone the [source code repository](https://github.com/saucelabs/isign) and
run the install script:

``` {.sourceCode .}
$ git clone https://github.com/saucelabs/isign.git
$ cd isign
$ sudo ./INSTALL.sh
```

How to get started
------------------

All the libraries and tools that `isign` needs to run will work on both Linux
and Mac OS X. However, you will need a Mac to export your Apple developer
credentials.

If you're like most iOS developers, credentials are confusing -- if so check out
the [documentation on credentials](https://github.com/saucelabs/isign/blob/master/docs/credentials.rst) on Github.

You should have a key and certificate in
[Keychain Access](https://en.wikipedia.org/wiki/Keychain_(software)),
and a provisioning profile associated with that certificate, that you
can use to sign iOS apps for one or more of your own iOS devices.

In Keychain Access, open the *Certificates*. Find the certificate you use to sign apps.
Right click on it and export the key as a `.p12` file, let's say `Certificates.p12`. If Keychain
asks you for a password to protect this file, just leave it blank.

Next, let's extract the key and certificate you need, into a standard PEM format.

``` {.sourceCode .}
$ isign_export_creds.sh ~/Certificates.p12
```

If you get prompted for a password, just press `Return`.

By default, `isign_export_creds.sh` will put these files into `~/.isign`, which is
the standard place to put `isign` configuration files.

Finally, you need a provisioning profile from the Apple Developer Portal that uses
the same certificate. If you've never dealt with this, the provisioning profile is
what tells the phone that you Apple has okayed you installing apps onto this particular phone.

If you develop with XCode, you might have a provisioning profile already.
On the Mac where you develop with XCode, try running the `isign_guess_mobileprovision.sh` script.
If you typically have only a few provisioning profiles and install on one phone, it might find it.

Anyway, once you have a `.mobileprovision` file, move it to `~/.isign/isign.mobileprovision`.

The end result should look like this:

``` {.sourceCode .}
$ ls -l ~/.isign
-r--r--r--    1 alice  staff  2377 Sep  4 14:17 certificate.pem
-r--r--r--    1 alice  staff  9770 Nov 23 13:30 isign.mobileprovision
-r--------    1 alice  staff  1846 Sep  4 14:17 key.pem
```

And now you're ready to start re-signing apps!

How to use isign
----------------

If you've installed all the files in the proper locations above, then `isign` can be now invoked
on any iOS `.app` directory, or `.ipa` archive, or `.app.zip` zipped directory. For example:

``` {.sourceCode .}
$ isign -o resigned.ipa my.ipa
archived Ipa to /home/alice/resigned.ipa
```

You can also call it from Python:

``` {.sourceCode .python}
from isign import isign

isign.resign("my.ipa", output_path="resigned.ipa")
```

isign command line arguments
----------------------------

``` {.sourceCode .}
# Resigning by specifying all credentials, input file, and output file
$ isign -c /path/to/mycert.pem -k ~/mykey.pem -p path/to/my.mobileprovision \
        -o resigned.ipa original.ipa

# Resigning, with credentials under default filenames in ~/.isign - less to type!
$ isign -o resigned.ipa original.ipa

# Modify Info.plist properties in resigned app
$ isign -i CFBundleIdentifier=com.example.myapp,CFBundleName=MyApp -o resigned.ipa original.ipa

# Display Info.plist properties from an app as JSON
$ isign -d my.ipa

# Get help
$ isign -h
```

**-a &lt;path&gt;, --apple-cert &lt;path&gt;**

Path to Apple certificate in PEM format. This is already included in the library, so you will likely
never need it. In the event that the certificates need to be changed, See the [Apple Certificate documentation](docs/applecerts.md).

**-c &lt;path&gt;, --certificate &lt;path&gt;**

Path to your certificate in PEM format. Defaults to `$HOME/.isign/certificate.pem`.

**-d, --display**

For the application path, display the information property list (Info.plist) as JSON.
        
**-e, --entitlements**

Use alternate entitlements,         '-e', '--entitlements',



**-h, --help**

Show a help message and exit.

**-i, --info**

While resigning, add or update info in the application's information property list (Info.plist).
Takes a comma-separated list of key=value pairs, such as
`CFBundleIdentifier=com.example.app,CFBundleName=ExampleApp`. Use with caution!
See Apple documentation for [valid Info.plist keys](https://developer.apple.com/library/ios/documentation/General/Reference/InfoPlistKeyReference/Introduction/Introduction.html).

**-k &lt;path&gt;, --key &lt;path&gt;**

Path to your private key in PEM format. Defaults to `$HOME/.isign/key.pem`.

**-n &lt;directory&gt;, --credentials &lt;directory&gt;**

Equivalent to:

``` {.sourceCode .}
-k <directory>/key.pem 
-c <directory>/certificate.pem 
-p <directory>/isign.mobileprovision
```

**-o &lt;path&gt;, --output &lt;path&gt;**

Path to write the re-signed application. Defaults to `out` in your current working directory.

**-p &lt;path&gt;, --provisioning-profile &lt;path&gt;**

Path to your provisioning profile. This should be associated with your certificate. Defaults to
`$HOME/.isign/isign.mobileprovision`.

**-v, --verbose**

More verbose logs will be printed to STDERR.

**Application path**

The app to be resigned is specified on the command line after other arguments. The application path is
typically an IPA, but can also be a `.app` directory or even a zipped `.app` directory. When
resigning, `isign` will always create an archive of the same type as the original.

Contributing
------------

Sauce Labs open source projects have a [Code of Conduct](CONDUCT.md). In short, we try to respect each other,
listen, and be helpful.

Development happens on [our Github repository](https://github.com/saucelabs/isign). File an issue, or fork the code!

You'll probably want to create some kind of python virtualenv, so you don't have to touch your system python or its
libraries. [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/) is a good tool for this.

Then, just do the following:

``` {.sourceCode .}
$ git clone https://github.com/saucelabs/isign.git
$ cd isign
$ dev/setup.sh 
$ ./run_tests.sh
```

If the tests don't pass please [file an issue](https://github.com/saucelabs/isign/issues). Please keep the tests up to date as you develop.

Note: some tests require Apple's
[codesign](https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man1/codesign.1.html)
to run, so they are skipped unless you run them on a Macintosh computer with developer tools.

Okay, if all the tests passed, you now have an 'editable' install of isign. Any edits to this repo will affect (for instance)
how the isign command line tool works.

Sauce Labs supports ongoing public `isign` development. `isign` is a part of our infrastructure
for the [iOS Real Device Cloud](https://saucelabs.com/press-room/press-releases/sauce-labs-expands-mobile-test-automation-cloud-with-the-addition-of-real-devices-1),
which allows customers to test apps and websites on real iOS devices. `isign` has been successfully re-signing submitted customer apps in production
since June 2015.

More documentation
------------------

See the [docs](docs) directory of this repository for random stuff that didn't fit here.

Authors
-------

[Neil Kandalgaonkar](https://github.com/neilk) is the main developer and maintainer.

Proof of concept by [Steven Hazel](https://github.com/sah) and Neil Kandalgaonkar.

Reference scripts using Apple tools by [Michael Han](https://github.com/mhan).
