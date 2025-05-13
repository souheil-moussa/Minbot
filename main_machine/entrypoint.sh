
#!/bin/bash

# Ensure the directory exists
mkdir -p /usr/local/apache2/out

# Create the file if it doesn't exist
touch /usr/local/apache2/out/livemeetingminutes.txt

# Create the symlink if it doesn't exist
if [ ! -L /usr/local/apache2/htdocs/livemeetingminutes.txt ]; then
    ln -s /usr/local/apache2/out/livemeetingminutes.txt /usr/local/apache2/htdocs/livemeetingminutes.txt
fi

# Start your usual processes
/usr/local/apache2/auto_convert.sh &

# Start Apache in the foreground
httpd-foreground
