`HMLLDB` is a collection of LLDB commands to assist in the debugging of iOS apps.  
[中文介绍](https://juejin.cn/post/6922784750986297352)

## Features
- Non-intrusive. Your iOS project does not need to be modified
- All commands support real device and simulator
- All commands support Objective-C and Swift project
- Some commands provide interactive UI within the APP

## Requirements
- Xcode 14.0
- 64-bit simulator or real device, iOS 11.0+
- Debug configuration (or ***Optimization Level*** set [-O0]/[-Onone])

## Installation
1. Download all the files. I recommend you to clone the repository.
2. Open  (or create) `~/.lldbinit` file, and append the following lines to the end of the file: 
```
command script import /path/to/HMLLDB.py
```
For example, this is the command in my computer:   
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
| bpframe        | Set a breakpoint that stops only when the specified stack keyword is matched |
| bpmethod       | Set a breakpoint that stops when the next OC method is called(via objc_msgSend) |
| rc             | Show general purpose registers changes |
| rr             | Show the contents of register values from the current frame |
| tracefunction  | Trace functions step by step until the next breakpoint is hit |
| traceinstruction | Trace instructions step by step until the next breakpoint is hit |
| pfont          | Print all font names supported by the device |
| plifecycle     | Print life cycle of UIViewController |
| redirect       | Redirect stdout/stderr |
| push           | Find UINavigationController in keyWindow then push a specified UIViewController |
| showhud        | Display the debug HUD on the key window. It shows the memory usage, CPU utilization and FPS of the main thread |
| sandbox        | Present a sandbox browser that can share and delete files |
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

### bpframe
Set a  breakpoint that stops only when the specified stack keyword is matched.    
```
Syntax:
bpframe [--one-shot] <symbol or function> <stack keyword 1> <stack keyword 2> ... <stack keyword n>
bpframe [--one-shot] --address <address> <stack keyword 1> <stack keyword 2> ... <stack keyword n>

# Stop when "viewDidAppear:" is hit and the call stack contains "customMethod"
(lldb) bpframe viewDidAppear: customMethod

# --address/-a; Set breakpoint at the address(hexadecimal).
# Stop when "0x1025df6c0" is hit and the call stack contains "customMethod"
(lldb) bpframe -a 0x1025df6c0 customMethod

# --one-shot/-o; The breakpoint is deleted the first time it stop.
(lldb) bpframe -o viewDidAppear: customMethod
(lldb) bpframe -o -a 0x1025df6c0 customMethod
```

### bpmethod
Set a breakpoint that stops when the next OC method is called(via objc_msgSend).    
When debugging the assembly instruction, it is very troublesome to see the `objc_msgSend` instruction. I usually want to jump the implementation of the method, but it is very inconvenient to find it. This command can solve this problem.     

```
# I want to step into implementation of the method, not the objc_msgSend function!!!
0x10075a574 <+64>: bl     0x10075a95c       ; symbol stub for: objc_msgSend

# Solution
(lldb) bpmethod
[HMLLDB] Done! You can continue program execution.

# --continue/-c; Continue program execution after executing bpmethod
(lldb) bpmethod -c
```

### rc
Show general purpose registers changes after stepping over instruction.    
```
(lldb) rc
[HMLLDB] Get registers for the first time.

// After you step over instruction, then execute the 'rc' command 
(lldb) rc
0x10431a3cc <+16>:  mov    x1, x2
        x1:0x000000010431aa94 -> 0x000000010490be50
        pc:0x000000010431a3cc -> 0x000000010431a3d0  Demo`-[ViewController clickBtn:] + 20 at ViewController.m:24
```

### rr
Show the contents of register values from the current frame.   
```
// Alias for 'register read'
(lldb) rr

// Alias for 'register read -a'
(lldb) rr -a

// Show [sp, (sp + offset)] address value after execute 'register read'
(lldb) rr -s 64
General Purpose Registers:
        x0 = 0x000000016dc24e48
        x1 = 0x0000000000000000
        x2 = 0x0000000129d0fd70
        x3 = 0x0000000281a30000
        x4 = 0x0000000281a30000
        x5 = 0x0000000281a30000
        x6 = 0x0000000000000000
        x7 = 0x000000016dc24aae
        x8 = 0x0000000000000006
        x9 = 0x0000000000000002
       x10 = 0x000000013a0efd77
       x11 = 0x01ff00012d00b800
       x12 = 0x0000000000000042
       x13 = 0x000000012d00bc10
       x14 = 0x00000001ba0ec000
       x15 = 0x0000000213521b88  (void *)0x0000000213521b60: UIButton
       x16 = 0x00000001d31fa170  libobjc.A.dylib`objc_release
       x17 = 0x00000002162b2f90  (void *)0x00000001d31fa170: objc_release
       x18 = 0x0000000000000000
       x19 = 0x0000000281a30000
       x20 = 0x0000000129d0fd70
       x21 = 0x00000001021de9d0  "clickBtn:"
       x22 = 0x0000000129d0a7a0
       x23 = 0x00000001021de9d0  "clickBtn:"
       x24 = 0x0000000213536800  UIKitCore`UIApp
       x25 = 0x0000000000000000
       x26 = 0x00000002047c18ff  
       x27 = 0x0000000281a30000
       x28 = 0x0000000000000001
        fp = 0x000000016dc24e60
        lr = 0x00000001021de170  Demo`-[ViewController clickBtn:] + 52 at ViewController.m:29
        sp = 0x000000016dc24e30
        pc = 0x00000001021de178  Demo`-[ViewController clickBtn:] + 60 at ViewController.m:31:1
      cpsr = 0x80001000

0x16dc24e30: 0x0000000281a30000
0x16dc24e38: 0x000000016dc24e48
0x16dc24e40: 0x0000000000000000
0x16dc24e48: 0x0000000129d0fd70
0x16dc24e50: 0x00000001021de9d0 "clickBtn:"
0x16dc24e58: 0x0000000129d0a7a0
0x16dc24e60: 0x000000016dc24e90
0x16dc24e68: 0x00000001bcd84f1c UIKitCore`-[UIApplication sendAction:to:from:forEvent:] + 100
0x16dc24e70: 0x0000000281a30000
```

### tracefunction
Trace functions step by step until the next breakpoint is hit.   
For example, if you set the following two breakpoints:   
![tracefunction](./img/tracefunction.jpg)

When you hit the first breakpoint, enter the `tracefunction` command   
```
(lldb) tracefunction
[HMLLDB] ==========Begin========================================================
Demo`-[ViewController buttonAction] + 24 at ViewController.m:28:25
Demo`-[ViewController buttonAction] + 24 at ViewController.m:28:25
Demo`symbol stub for: objc_alloc + 8
libobjc.A.dylib`objc_alloc + 20
libobjc.A.dylib`_objc_rootAllocWithZone + 36
libobjc.A.dylib`symbol stub for: calloc + 12
libsystem_malloc.dylib`calloc + 20
libsystem_malloc.dylib`_malloc_zone_calloc + 84
libsystem_malloc.dylib`default_zone_calloc + 32
libsystem_malloc.dylib`nanov2_calloc + 156
libsystem_malloc.dylib`nanov2_allocate + 124
libsystem_malloc.dylib`nanov2_allocate + 340
libsystem_malloc.dylib`symbol stub for: _platform_memset + 8
libsystem_platform.dylib`_platform_memset + 208
libsystem_malloc.dylib`nanov2_allocate + 460
libsystem_malloc.dylib`nanov2_calloc + 172
libsystem_malloc.dylib`_malloc_zone_calloc + 132
libobjc.A.dylib`_objc_rootAllocWithZone + 100
Demo`-[ViewController buttonAction] + 40 at ViewController.m:28:24
Demo`symbol stub for: objc_msgSend + 8
libobjc.A.dylib`objc_msgSend + 76
libobjc.A.dylib`-[NSObject init]
Demo`-[ViewController buttonAction] + 60 at ViewController.m:29:1
[HMLLDB] ==========End========================================================
[HMLLDB] Instruction count: 285
[HMLLDB] Function count: 23
[HMLLDB] Start time: 18:35:35
[HMLLDB] Stop time: 18:35:36
Process 11646 stopped
* thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 2.1
    frame #0: 0x0000000104216338 Demo`-[ViewController buttonAction](self=0x0000000104704d70, _cmd="buttonAction") at ViewController.m:29:1
   26    
   27    - (void)buttonAction {
   28        NSObject *object = [[NSObject alloc] init];
-> 29    }
      ^
   30    
   31    
   32    
Target 0: (Demo) stopped.


// Up to 500 functions will be printed
(lldb) tracefunction -m 500
...
```

### traceinstruction
Trace instructions step by step until the next breakpoint is hit.   
For example, if you set the following two breakpoints:   
![tracefunction](./img/tracefunction.jpg)

When you hit the first breakpoint, enter the `traceinstruction` command   
```
(lldb) traceinstruction
[HMLLDB] ==========Begin========================================================
Demo`-[ViewController buttonAction] + 24 at ViewController.m:28:25		ldr	x0, [x8, #0xe40]
Demo`symbol stub for: objc_alloc		nop	
Demo`symbol stub for: objc_alloc + 4		ldr	x16, #0x171c			; (void *)0x00000001b006c918: objc_alloc
Demo`symbol stub for: objc_alloc + 8		br	x16
libobjc.A.dylib`objc_alloc		cbz	x0, 0x1b006c930			; <+24>
libobjc.A.dylib`objc_alloc + 4		ldr	x8, [x0]
libobjc.A.dylib`objc_alloc + 8		and	x8, x8, #0xffffffff8
libobjc.A.dylib`objc_alloc + 12		ldrb	w8, [x8, #0x1d]
libobjc.A.dylib`objc_alloc + 16		tbz	w8, #0x6, 0x1b006c934			; <+28>
libobjc.A.dylib`objc_alloc + 20		b	0x1b006c3e8			; _objc_rootAllocWithZone
libobjc.A.dylib`_objc_rootAllocWithZone		pacibsp	
libobjc.A.dylib`_objc_rootAllocWithZone + 4		stp	x20, x19, [sp, #-0x20]!
libobjc.A.dylib`_objc_rootAllocWithZone + 8		stp	x29, x30, [sp, #0x10]
libobjc.A.dylib`_objc_rootAllocWithZone + 12		add	x29, sp, #0x10
libobjc.A.dylib`_objc_rootAllocWithZone + 16		mov	x19, x0
libobjc.A.dylib`_objc_rootAllocWithZone + 20		ldrh	w20, [x0, #0x1c]
libobjc.A.dylib`_objc_rootAllocWithZone + 24		and	x1, x20, #0x1ff0
libobjc.A.dylib`_objc_rootAllocWithZone + 28		cbz	w1, 0x1b006c450			; <+104>
libobjc.A.dylib`_objc_rootAllocWithZone + 32		mov	w0, #0x1
libobjc.A.dylib`_objc_rootAllocWithZone + 36		bl	0x1b0095518			; symbol stub for: calloc
libobjc.A.dylib`symbol stub for: calloc		adrp	x17, 274573
libobjc.A.dylib`symbol stub for: calloc + 4		add	x17, x17, #0xe70
libobjc.A.dylib`symbol stub for: calloc + 8		ldr	x16, [x17]
libobjc.A.dylib`symbol stub for: calloc + 12		braa	x16, x17
libsystem_malloc.dylib`calloc		mov	x2, x1
libsystem_malloc.dylib`calloc + 4		mov	x1, x0
libsystem_malloc.dylib`calloc + 8		adrp	x0, 292190
libsystem_malloc.dylib`calloc + 12		add	x0, x0, #0x0
libsystem_malloc.dylib`calloc + 16		mov	w3, #0x1
libsystem_malloc.dylib`calloc + 20		b	0x1a9605e04			; _malloc_zone_calloc
libsystem_malloc.dylib`_malloc_zone_calloc		pacibsp	
libsystem_malloc.dylib`_malloc_zone_calloc + 4		stp	x24, x23, [sp, #-0x40]!
...
...
...
libobjc.A.dylib`objc_msgSend		cmp	x0, #0x0
libobjc.A.dylib`objc_msgSend + 4		b.le	0x1b0068ff0			; <+208>
libobjc.A.dylib`objc_msgSend + 8		ldr	x13, [x0]
libobjc.A.dylib`objc_msgSend + 12		and	x16, x13, #0x7ffffffffffff8
libobjc.A.dylib`objc_msgSend + 16		mov	x10, x0
libobjc.A.dylib`objc_msgSend + 20		movk	x10, #0x6ae1, lsl #48
libobjc.A.dylib`objc_msgSend + 24		autda	x16, x10
libobjc.A.dylib`objc_msgSend + 28		mov	x15, x16
libobjc.A.dylib`objc_msgSend + 32		ldr	x11, [x16, #0x10]
libobjc.A.dylib`objc_msgSend + 36		tbnz	w11, #0x0, 0x1b0068fa0			; <+128>
libobjc.A.dylib`objc_msgSend + 40		and	x10, x11, #0xffffffffffff
libobjc.A.dylib`objc_msgSend + 44		eor	x12, x1, x1, lsr #7
libobjc.A.dylib`objc_msgSend + 48		and	x12, x12, x11, lsr #48
libobjc.A.dylib`objc_msgSend + 52		add	x13, x10, x12, lsl #4
libobjc.A.dylib`objc_msgSend + 56		ldp	x17, x9, [x13], #-0x10
libobjc.A.dylib`objc_msgSend + 60		cmp	x9, x1
libobjc.A.dylib`objc_msgSend + 64		b.ne	0x1b0068f70			; <+80>
libobjc.A.dylib`objc_msgSend + 68		eor	x10, x10, x1
libobjc.A.dylib`objc_msgSend + 72		eor	x10, x10, x16
libobjc.A.dylib`objc_msgSend + 76		brab	x17, x10
libobjc.A.dylib`-[NSObject init]		ret	
Demo`-[ViewController buttonAction] + 44 at ViewController.m:28:24		mov	x8, x0
Demo`-[ViewController buttonAction] + 48 at ViewController.m:28:24		add	x0, sp, #0x8
Demo`-[ViewController buttonAction] + 52 at ViewController.m:28:15		str	x8, [sp, #0x8]
Demo`-[ViewController buttonAction] + 56 at ViewController.m:28:15		mov	x1, #0x0
Demo`-[ViewController buttonAction] + 60 at ViewController.m:29:1		bl	0x104c3e95c			; symbol stub for: objc_storeStrong
[HMLLDB] ==========End========================================================
[HMLLDB] Instruction count: 291
[HMLLDB] Start time: 19:34:59
[HMLLDB] Stop time: 19:35:00
Process 30877 stopped
* thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 2.1
    frame #0: 0x0000000104c3e338 Demo`-[ViewController buttonAction](self=0x00000001052092c0, _cmd="buttonAction") at ViewController.m:29:1
   26  	
   27  	- (void)buttonAction {
   28  	    NSObject *object = [[NSObject alloc] init];
-> 29  	}
    	^
   30  	
   31  	
   32  	
Target 0: (Demo) stopped.


// Up to 8000 instructions will be printed
(lldb) traceinstruction -m 8000
...
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
Display the debug HUD on the *keyWindow*. It shows the memory usage, CPU utilization and FPS of the main thread.   
![img5](./img/img5.jpg)

Tap the debug HUD will present a new view controller, and its function will be introduced later.   
![img6](./img/img6.jpg)


### sandbox
Present a sandbox browser that can access Bundle Container and  Data Container. You can delete files in the Data Container and share files with AirDrop.   
It takes a few seconds to call the command for the first time.   
![img7](./img/img7.gif)
This is an example of sharing files with AirDrop.   
![share_AirDrop](./img/share_AirDrop.jpg)


### inspect
Inspect UIView of the current page.   
![img8](./img/img8.jpg)

### request
Print http/https request automatically.(Except WKWebView)   
The same request may be printed several times.    
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