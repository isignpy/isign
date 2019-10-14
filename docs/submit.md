# Submitting a resigned app to Apple

Unfortunately, when using isign, you will not be able to simply use XCode to figure out signing and submitting

Here are some possible procedures for doing this. They worked as of October 2019 with current MacOS and the 
Apple Developer ecosystem.

## Manual procedure

We assume you are using the `bash` shell on a contemporary MacOS computer.

The basic idea here is that we will resign the app locally, and then upload it to App Store Connect via `xcrun altool`.

### Preparation (one-time only)

Add your Apple Developer Account App Store username as an environment variable to your `.bash_profile`. 
In most cases, this is identical to your Apple Developer Account username, and is usually an email address.

```bash
export APP_STORE_USERNAME=you@your.domain
```

You might also want to add this to your `.bash_profile`, to set up paths to additional tools such as `altool`.
 
```bash
xcode-select -r     # to set up paths. 
```

With your web browser, on `https://developer.apple.com/`, prepare your accounts and certificates for distribution.

We'll also need to set up an "app password" to be used by `altool`. Log in to `https://appleid.apple.com/`, and
scroll to the "Security" section. Set up an app password, and label it "altool". Store this password somewhere 
secure. 

### Password security

Later on you're going to need to use this password on the command line. _This is a potential 
security vulnerability_. The command and its argumetns can be observed by other processes on your machine, and 
it will automatically be stored in your `.bash_history`.

So, the best practice would be to store it someplace secure, and then obtain it for use on the command line, 
in some way that doesn't leave traces.

Here are a couple of options:

* Apple Keychain: If you choose to store the above password in the Apple Keychain, there is a way to use it directly
  with the command line for `altool` where you would normally use a password. See `man altool` for the details.
  
* Other password managers: you can simply cut & paste from another password manager app. Personally, I use the 
  LastPass `lastpass-cli` package. In my LastPass vault, I made a pseudo-website called "developer.apple.com-altool" 
  without a username and using the altool password. Then I can do something like this:
```bash
$ export APP_STORE_PASSWORD=$(lpass show developer.apple.com-altool --password)
```

In the following examples, we'll assume that (somehow) the password exists in the environment variable 
`$APP_STORE_PASSWORD`.

### When you build your app

Open your app project in XCode.

When you submit to Apple, you need to keep bumping the bundle version. If you don't have some automatic 
way to do that, you can manually edit the file `Info.plist`. A simple thing to do is to call your first version 0.01,
then increment to 0.02, etc. Enter the same string in:

* Bundle versions string, short
* Bundle version

At the top of the windowm select “Generic iOS Device” as your build target.
 
Select “Product > Archive”.

This will compile your project, then pop up the Archives window.

Select the archive you just made and press the “Distribute App” button.

Select “App Store Connect”, and press “Next”.

Select “Export”,  and press “Next”.

Select the appropriate options for bitcode and symbol retention, and press  “Next”.

Select “Automatically manage signing”. (We're going to let XCode sign it once for us, with some developer identity,
and resign it later with `isign`.)

XCode will present you with a summary of all these options. Confirm them by pressing “Export” and select a 
destination directory.

In the terminal, cd to the directory you created, there should be an IPA there.

Use `isign` to resign this IPA, for example

```bash
$ isign -o resigned.ipa original.ipa
```

Lastly (and this is what we've been building up to...) use `altool` to validate and submit:

```bash
$ xcrun altool —validate-app --file ./resigned.ipa --username "$APP_STORE_USERNAME" --password "$APP_STORE_PASSWORD"
$ xcrun altool --upload-app --file ./resigned.ipa --username "$APP_STORE_USERNAME" --password "$APP_STORE_PASSWORD"

```


## Semi-automated procedure

TBD - add an action to XCode build pipeline