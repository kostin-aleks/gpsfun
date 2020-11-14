form_page = """
    <html>
    <head>
      <title>Command Test</title>
    </head>

    <body>
      <form action='add_job' method='post'>
        Command (with absolute path):
        <p><input type='text' name='command' /></p>

        Arguments (split space):
        <p><input type='text' name='args' /></p>
	
	Input File:
	<div>
	  <label>filename:</label>
	  <p><input type="text" name="in_filename" size="50" value="" /></p>
	  <label>file url:</label>
	  <p><input type="text" name="in_file_url" size="50" value="" /></p>
	  <label>file path:</label>
	  <p><input type="text" name="in_file_path" size="50" value="" /></p>
	</div>

	Input File:
	<div>
	  <label>filename:</label>
	  <p><input type="text" name="in_filename" size="50" value="" /></p>
	  <label>file url:</label>
	  <p><input type="text" name="in_file_url" size="50" value="" /></p>
	  <label>file path:</label>
	  <p><input type="text" name="in_file_path" size="50" value="" /></p>
	</div>

        <!--
	Output File:
	<div>
	  <label>filename:</label>
	  <p><input type="text" name="out_filename" size="50" value="" /></p>
	  <label>file path:</label>
	  <p><input type="text" name="out_file_path" size="50" value="" /></p>
	</div>
        -->

      <input type='submit' value='Run command'/>
    
      </form>

    </body>

    </html>
    
"""

check_status_page = """
    <html>
    <head>
      <title>Command Status</title>
    </head>

    <body>
      <form action='check_status' method='post'>
	Command: %(command)s %(args)s<br />
	Status: %(status)s<br />
        Job key:
        <p><input type='text' name='key' value='%(secure_key)s' /></p>

      <input type='submit' value='Check status'/>
    
      </form>

    </body>

    </html>


"""

job_add_success = """
    <html>
    <head>
      <title>Add job success</title>
    </head>

    <body>
      <form action='check_status' method='post'>
        Command added to order successfully<br />
        Job key:
        <p><input type='text' name='key' value='%(secure_key)s' /></p>

      <input type='submit' value='Check status'/>
    
      </form>

    </body>

    </html>


"""

command_res_page = """

    <html>
    <head>
      <title>Command Results</title>
    </head>

    <body>
        Command: %(command)s %(args)s<br />
        Status: Finished<br />
        Results:
        %(results)s
    
    </body>

    </html>

"""
