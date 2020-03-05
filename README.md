
[![CircleCI](https://circleci.com/gh/isignpy/isign/tree/master.svg?style=svg)](https://circleci.com/gh/isignpy/isign/tree/master)

isign
=====

A tool and library to re-sign iOS applications, without proprietary Apple software.

For example, an iOS app in development would probably only run on the developer's iPhone. `isign` can alter the app so that it can run on another developer's iPhone.

Apple tools already exist to do this. But with `isign`, now you have many more options:
 
 * Sign your app on an operating systems like Linux. This can be far more convenient for continuous integration (CI).
 * Run a test lab where you accept compiled apps from other organizations, and resign them for use on a fleet of real devices. 
 * Do things that are impossible with the Apple tools, such as storing your secrets in something that isn't the Keychain, or using a hardware security module that signs objects without you ever knowing the key.


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

The easiest method is to use `git` to clone the [source code repository](https://github.com/isignpy/isign) and
run the install script, then install dependencies with `pipenv`. 

If you want to run the tests or develop with isign, skip ahead to [Contributing][#contributing]

```shell script
$ git clone https://github.com/isignpy/isign.git
$ cd isign
$ ./INSTALL.sh    # very important if you are on MacOS
$ pipenv --two install
$ pipenv shell
```

How to get started
------------------

All the libraries and tools that `isign` needs to run will work on both Linux
and Mac OS X. However, you will need a Mac to export your Apple developer
credentials.

If you're like most iOS developers, credentials are confusing -- if so check out
the [documentation on credentials](docs/credentials.md) on Github.

You should have a key and certificate in
[Keychain Access](https://en.wikipedia.org/wiki/Keychain_(software)),
and a provisioning profile associated with that certificate, that you
can use to sign iOS apps for one or more of your own iOS devices.

In Keychain Access, open the *Certificates*. Find the certificate you use to sign apps.
Right click on it and export the key as a `.p12` file, let's say `Certificates.p12`. If Keychain
asks you for a password to protect this file, just leave it blank.

Next, let's extract the key and certificate you need, into a standard PEM format.

``` bash
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

Anyway, once you have a `.mobileprovision` file, move it to `~/.isign/isign.mobileprovision`. (It doesn't actually matter what the 
name of this file is).

The end result should look like this:

```shell script
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

```shell script
$ isign -o resigned.ipa my.ipa
archived Ipa to /home/alice/resigned.ipa
```

You can also call it from Python:

```python
from isign import isign

isign.resign("my.ipa", output_path="resigned.ipa")
```

isign command line arguments
----------------------------

```shell script
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

**--adhoc**

Resign the app "ad hoc". This is a full signature, but with empty data. Simulator apps need to be signed this way.

**-c &lt;path&gt;, --certificate &lt;path&gt;**

Path to your certificate in PEM format. Defaults to `$HOME/.isign/certificate.pem`.

**-d, --display**

For the application path, display the information property list (Info.plist) as JSON.
        
**-e, --entitlements**

Use alternate entitlements. Normally, `isign` will discover entitlements from the provisioning profile. If you want to override the entitlements for a bundle, you can simply add an entitlements file formatted as a plist here on the command line. Entitlements files already specify which bundle they apply to, so you can add as many entitlements files as you wish.

**-h, --help**

Show a help message and exit.

**-i, --info**

While resigning, add or update info in the application's information property list (Info.plist).
Takes a comma-separated list of key=value pairs, such as
`CFBundleIdentifier=com.example.app,CFBundleName=ExampleApp`. Use with caution!
See Apple documentation for [valid Info.plist keys](https://developer.apple.com/library/ios/documentation/General/Reference/InfoPlistKeyReference/Introduction/Introduction.html).

Caveat: at present, this only works with the main executable.

**--inplace**

Resigns the application in place.

**-k &lt;path&gt;, --key &lt;path&gt;**

Path to your private key in PEM format. Defaults to `$HOME/.isign/key.pem`.

**-n &lt;directory&gt;, --credentials &lt;directory&gt;**

Pull all credentials, provisioning profiles, and entitlements from a directory. 

For example, if a that directory contained:

```shell script
certificate.pem
key.pem
myApp.mobileprovision
myApp.WatchKitApp.mobileprovision
myApp.WatchKitApp.entitlements
myApp.appex.entitlements
```

That would be equivalent to:

```shell script
-k key.pem 
-c certificate.pem 
-p myApp.mobileprovision
-p MyApp.WatchKitApp.mobileprovision
-e myApp.appex.entitlements
-e myApp.WatchKitApp.entitlements
```

**-o &lt;path&gt;, --output &lt;path&gt;**

Path to write the re-signed application. Defaults to `out` in your current working directory.

**-p &lt;path&gt;, --provisioning-profile &lt;path&gt;**

Path to your provisioning profile. This should be associated with your certificate. If not included, it will default to
`$HOME/.isign/isign.mobileprovision`.

You can include multiple provisioning profiles with repeated use of this option.

**--signer &lt;SignerModuleName.SignerClassName&gt;**

Name of alternate signer module. Must be discoverable via PYTHONPATH. See
[Signer Modules](docs/signer_modules.md) for more information.
  
**--signerArg &lt;foo=bar&gt;**

Keyword=value arguments for signer module. Can be repeated multiple 
times.

**--shallow**

Only resign the main executable.

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

Development happens on [our Github repository](https://github.com/isignpy/isign). File an issue, or fork the code!

You'll need [pipenv](https://docs.pipenv.org/en/latest/).

Then, just do the following:

``` {.sourceCode .}
$ git clone https://github.com/isignpy/isign.git
$ cd isign
$ ./INSTALL.sh 
$ pipenv --two install --dev
$ pipenv shell
```

If the tests don't pass please [file an issue](https://github.com/isignpy/isign/issues). Please keep the tests up to date as you develop.

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

[Neil Kandalgaonkar](https://neilk.net/) and [Steven Hazel](https://stevenhazel.org) are the primary authors and maintainers.

Reference scripts using Apple tools by [Michael Han](https://github.com/mhan).
