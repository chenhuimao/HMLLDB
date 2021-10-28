`HMLLDB` is a collection of LLDB commands to assist in the debugging of iOS apps.  
[中文介绍](https://juejin.cn/post/6922784750986297352)

## Features
- Non-intrusive. Your iOS project does not need to be modified
- All commands support real device and simulator
- All commands support Objective-C and Swift project
- Some commands provide interactive UI within the APP

## Requirements
- Xcode 13.1
- 64-bit simulator or real device, iOS 9.0+
- Debug configuration (or ***Optimization Level*** set [-O0]/[-Onone])

## Installation
1. Download all the files. I recommend cloning the repository.
2. Open up (or create) `~/.lldbinit` file, and append the following lines to the end of the file: 
```
command script import /path/to/HMLLDB.py
```
For example, the command in my computer:   
`command script import /Users/pal/Desktop/gitProjects/HMLLDB/commands/HMLLDB.py`

3. Restart Xcode, run your own iOS project, click `Pause program execution` to enter the LLDB debugging mode, enter the command `help`, if you see the commands described below, the installation is successful.

## Commands

| Command        | Description            |
| -------------- | ---------------------- |
| deletefile     | Delete the specified file in the sandbox |
| pbundlepath    | Print the path of the main bundle |
| phomedirectory | Print the path of the home directory("~") |
| fclass         | Find the class containing the input name(Case insensitive) |
| fsubclass      | Find the subclass of the input |
| fsuperclass    | Find the superclass of the input |
| fmethod        | Find the specified method in the method list, you can also find the method list of the specified class |
| methods        | Execute `[inputClass _methodDescription]` or `[inputClass _shortMethodDescription]` |
| properties     | Execute `[inputClass _propertyDescription]` |
| ivars          | Execute `[instance _ivarDescription]` |
| pfont          | Print all font names supported by the device |
| plifecycle     | Print life cycle of UIViewController |
| redirect       | Redirect stdout/stderr |
| push           | Find UINavigationController in keyWindow then push a specified UIViewController |
| showhud        | Display the debug HUD on the key window, it is showing the memory usage, CPU utilization and FPS of the main thread |
| sandbox        | Presenting a sandbox browser that can share and delete files |
| inspect        | Inspect UIView |
| request        | Print http/https request automatically |
| environment    | Show diagnostic environment. |
| ...            |                        |

All commands in the table can use `help <command>` to view the syntax and examples. For example, the output of `help fmethod`:
```
(lldb) help fmethod
     Find the method.  Expects 'raw' input (see 'help raw-input'.)

Syntax: fmethod

    Syntax:
        fmethod <methodName>  (Case insensitive.)
        fmethod [--class] <className>

    Options:
        --class/-c; Find all method in the class

    Examples:
        (lldb) fmethod viewdid
        (lldb) fmethod viewDidLayoutSubviews
        (lldb) fmethod -c UITableViewController

    This command is implemented in HMClassInfoCommands.py
```

## Example
Some examples use the demo in the [Kingfisher](https://github.com/onevcat/Kingfisher) project.  
**It is recommended to click `Pause program execution` to enter the LLDB debugging mode to execute commands, instead of executing commands by hitting breakpoints.**

### deletefile
It is recommended to re-run the project after executing the command, because some data is still in the memory.
```
# Delete all file in the sandbox
(lldb) deletefile -a

# Delete the "~/Documents" directory
(lldb) deletefile -d

# Delete the "~/Library" directory
(lldb) deletefile -l

# Delete the "~/tmp" directory
(lldb) deletefile -t

# Delete the "~/Library/Caches" directory
(lldb) deletefile -c

# Delete the "~Library/Preferences" directory
(lldb) deletefile -p

# Delete the specified file or directory
(lldb) deletefile -f path/to/fileOrDirectory
```

### pbundlepath & phomedirectory
```
# Print the path of the main bundle
(lldb) pbundlepath
[HMLLDB] /Users/pal/Library/Developer/CoreSimulator/Devices/D90D74C6-DBDF-4976-8BEF-E7BA549F8A89/data/Containers/Bundle/Application/84AE808C-6703-488D-86A2-C90004434D3A/Kingfisher-Demo.app

# Print the path of the home directory
(lldb) phomedirectory
[HMLLDB] /Users/pal/Library/Developer/CoreSimulator/Devices/D90D74C6-DBDF-4976-8BEF-E7BA549F8A89/data/Containers/Data/Application/3F3DF0CD-7B57-4E69-9F15-EB4CCA7C4DD8

# If it is running on the simulator, you can add the -o option to open path with Finder
(lldb) pbundlepath -o
(lldb) phomedirectory -o
```

### fclass & fsubclass & fsuperclass & fmethod
These commands are optimized for Swift, and the namespace can be omitted when entering the Swift class.   

`fclass`: Find all class names that contain the specified string.

```
(lldb) fclass NormalLoadingViewController
[HMLLDB] Waiting...
[HMLLDB] Count: 1 
Kingfisher_Demo.NormalLoadingViewController (0x102148fa8)

# Case insensitive
(lldb) fclass Kingfisher_Demo.im
[HMLLDB] Waiting...
[HMLLDB] Count: 2 
Kingfisher_Demo.ImageDataProviderCollectionViewController (0x102149a18)
Kingfisher_Demo.ImageCollectionViewCell (0x1021498e8)
```

`fsubclass`: Find all subclasses of a class.
```
(lldb) fsubclass UICollectionViewController
[HMLLDB] Waiting...
[HMLLDB] Subclass count: 10 
Kingfisher_Demo.InfinityCollectionViewController
Kingfisher_Demo.HighResolutionCollectionViewController
...
```

`fsuperclass`: Find the super class of a class.

```
(lldb) fsuperclass UIButton
[HMLLDB] UIButton : UIControl : UIView : UIResponder : NSObject

(lldb) fsuperclass KingfisherManager
[HMLLDB] Kingfisher.KingfisherManager : Swift._SwiftObject
```

`fmethod`: Find the specified method in the method list, you can also find the method list of the specified class.

```
# Find the specified method in the method list. Case insensitive.
(lldb) fmethod clear
[HMLLDB] Waiting...
[HMLLDB] Methods count: 3725 
(-) clearMemoryCache (0x10526f1c0)
	Type encoding:v16@0:8
	Class:Kingfisher.ImageCache
(-) accessibilityClearInternalData (0x1084ffd08)
	Type encoding:v16@0:8
	Class:NSObject
(+) _accessibilityClearProcessedClasses: (0x7fff2dc2cd25)
	Type encoding:v24@0:8@16
	Class:NSObject
...

# Option -c: Find the method list of the specified class. Case sensitive.
(lldb) fmethod -c ImageCache
[HMLLDB] Waiting...
[HMLLDB] Class: Kingfisher.ImageCache (0x1052f26f8)
Instance methods count: 3. Class method count: 0.
(-) cleanExpiredDiskCache (0x10526fa00)
	Type encoding:v16@0:8
(-) backgroundCleanExpiredDiskCache (0x105271330)
	Type encoding:v16@0:8
(-) clearMemoryCache (0x10526f1c0)
	Type encoding:v16@0:8
```

### methods & properties & ivars
`methods`: Execute `[inputClass _methodDescription]` or `[inputClass _shortMethodDescription]`
`properties`: Execute `[inputClass _propertyDescription]`
`ivars`: Execute `[instance _ivarDescription]`

These commands are optimized for Swift, and the namespace can be omitted when entering the Swift class.

```
# Syntax
methods [--short] <className/classInstance>
properties <className/classInstance>
ivars <Instance>

(lldb) methods NormalLoadingViewController
[HMLLDB] <Kingfisher_Demo.NormalLoadingViewController: 0x10d55ffa8>:
in Kingfisher_Demo.NormalLoadingViewController:
	Instance Methods:
		- (id) collectionView:(id)arg1 cellForItemAtIndexPath:(id)arg2; (0x10d523f30)
		- (long) collectionView:(id)arg1 numberOfItemsInSection:(long)arg2; (0x10d522a20)
		- (void) collectionView:(id)arg1 willDisplayCell:(id)arg2 forItemAtIndexPath:(id)arg3; (0x10d523af0)
		- (void) collectionView:(id)arg1 didEndDisplayingCell:(id)arg2 forItemAtIndexPath:(id)arg3; (0x10d522cb0)
		- (id) initWithCoder:(id)arg1; (0x10d522960)
...

# These commands can only be used for subclasses of NSObject
(lldb) methods KingfisherManager
[HMLLDB] KingfisherManager is not a subclass of NSObject

```

### pfont
Print all font names supported by the device.   
```
(lldb) pfont
[HMLLDB] Family names count: 81, font names count: 274
familyNames: Academy Engraved LET
	fontName: AcademyEngravedLetPlain
familyNames: Al Nile
	fontName: AlNile
	fontName: AlNile-Bold
familyNames: American Typewriter
	fontName: AmericanTypewriter
...
```

### plifecycle
Used to print the life cycle of UIViewController.   
In a non-intrusive way, and Xcode can set the console font color to make it clearer. It has become one of my favorite commands.   

Usage:  
1. Create a **Symbolic Breakpoint**, and then add the method to be printed in the **Symbol** line.(e.g.` -[UIViewController viewDidAppear:]`)
2. Add a **Action(Debugger Command)**, enter the `plifecycle` command
3. Check the option: **Automatically continue after evaluating actions**

I usually use the -i option to ignore some system-generated UIViewController.
![img1](./img/img1.jpg)

I often *Enable* `viewDidAppear:` and `dealloc` methods, and the other methods are set to *Disable* and started on demand, as shown below:
![img2](./img/img2.jpg)

Output in Xcode:
![img3](./img/img3.jpg)

It should be noted that there are two problems with this command.
1. Cause UIViewController switching lag.
2. The following warning may be triggered when starting the APP. You need to click `Continue program execution` in Xcode to let the APP continue to run.
```
Warning: hit breakpoint while running function, skipping commands and conditions to prevent recursion.
```
BTW, the source code provides other ways to use LLDB to print the life cycle.

### redirect
Redirect stdout/stder.
```
# You can redirect the output of Xcode to Terminal if you use the simulator
# Open the terminal, enter the "tty" command, you can get the path: /dev/ttys000
(lldb) redirect both /dev/ttys000
[HMLLDB] redirect stdout successful
[HMLLDB] redirect stderr successful
```

### push
Find UINavigationController in *keyWindow* then push a specified UIViewController.   
Notice: `push MyViewController` needs to execute `[[MyViewController alloc] init]` first. If the initializer of the class requires parameters, or the class needs to pass parameters after initialization, this command may cause errors.   
The GIF demo didn't use **Kingfisher** because the UIViewController in the demo depends on the storyboard.   
![img4](./img/img4.gif)


### showhud
Display the debug HUD on the *keyWindow*, it is showing the memory usage, CPU utilization and FPS of the main thread.
![img5](./img/img5.jpg)

Tapping the debug HUD will present a new view controller, and its function will be introduced later. 
![img6](./img/img6.jpg)


### sandbox
Presenting a sandbox browser that can share and delete files.  
It takes a few seconds to call the command for the first time.
![img7](./img/img7.gif)


### inspect
Inspect UIView of the current page.   
![img8](./img/img8.jpg)

### request
Print http/https request automatically.(Except WKWebView)   
The same request may be printed multiple times, please judge for yourself.   
![request](./img/request.gif)

### environment
Show diagnostic environment.   
You can see that one of items is `[Git commit hash]`, which is one of the reasons why clone repository is recommended.

```
(lldb) environment
[HMLLDB] [Python version] 3.8.2 (default, Nov  4 2020, 21:23:28) 
		[Clang 12.0.0 (clang-1200.0.32.28)]
[HMLLDB] [LLDB version] lldb-1200.0.44.2
		Apple Swift version 5.3.2 (swiftlang-1200.0.45 clang-1200.0.32.28)
[HMLLDB] [Target triple] x86_64h-apple-ios-simulator
[HMLLDB] [Git commit hash] 088f654cb158ffb16019b2deca5dce36256837ad
[HMLLDB] [Optimized] False: 28  True: 0
[HMLLDB] [Xcode version] 1230
[HMLLDB] [Xcode build version] 12C33
[HMLLDB] [Model identifier] x86_64
[HMLLDB] [System version] iOS 13.0
```

## If an error occurs 
Just-in-time compilation via LLDB is not stable. If an error occurs, please check in order according to the following steps.   
1. pull the latest code. Check the Xcode version, `HMLLDB` generally only adapts to the latest Xcode version. 
2. Open the `~/.lldbinit` file and make sure to import the `HMLLDB.py` at the end of the file so that its commands are not overwritten.
3. After launching the APP, click `Pause program execution` to enter the LLDB debugging mode to execute commands, instead of executing commands by hitting breakpoints. (In general, you can execute commands by hitting breakpoints)
4. Restart Xcode can solve most problems. 
5. Restart the computer.
6. After completing the above steps, the command still fails. Please copy the error and post it to Issue, and execute the `environment` command, its output should also be posted to Issue. 

## License

HMLLDB is released under the MIT license. See LICENSE for details.