binterceptor
------------
(binary interceptor)

Binterceptor is a hacky proxy built for analyzing binary network protocols. It allows the operator to intercept data as it passes through their machine. Once the data is intercepted the operator has the ability to "forward", "edit", or "drop" the data.

* __forward__: send the data directly to the host specified on the commandline
* __edit__: modify the data contained in the intercepted packet using $EDITOR (or nano). The data is presented just as ascii data, and behaves how you would expect a hexeditor to.
* __drop__: ignores the intercepted packet. If this option is chosen binterceptor will begin listening for new client data regardless of whether it was client or server data which was dropped.

Installation:

<pre> $ sudo python setup.py install </pre>
