import cgi
import cgitb
import http.cookies
import os

cgitb.enable()

def set_cookie(name, value, expires=None):
    cookie = f"{name}={value};"
    if expires:
        cookie += f"expires={expires};"
    print(f"Set-Cookie: {cookie}")

def delete_all_cookies():
    print("Set-Cookie: form_count=0; expires=Thu, 01 Jan 1970 00:00:00 GMT;")

form = cgi.FieldStorage()

name = form.getvalue("name")
email = form.getvalue("email")
subscribe = form.getvalue("subscribe")
gender = form.getvalue("gender")

if "HTTP_COOKIE" in os.environ:
    cookies = os.environ["HTTP_COOKIE"].split("; ")
    for cookie in cookies:
        if "=" in cookie:
            cookie_name, cookie_value = cookie.split("=")
            if cookie_name == "form_count":
                form_count = int(cookie_value)
                break
    else:
        form_count = 0
else:
    form_count = 0

form_count += 1
set_cookie("form_count", str(form_count))

print("Content-Type: text/html\n")

print("<html>")
print("<head><title>Form Processing</title></head>")
print("<body>")
print("<h1>Form Processing with CGI</h1>")

print("<h2>Form Data</h2>")
print(f"<p>Name: {name}</p>")
print(f"<p>Email: {email}</p>")
print(f"<p>Subscribe: {subscribe}</p>")
print(f"<p>Gender: {gender}</p>")

print(f"<p>Form submitted {form_count} times.</p>")

print("<h2>Delete Cookies</h2>")
print("<form method='post' action='form_handler.py'>")
print("<input type='submit' name='delete_cookies' value='Delete All Cookies'>")
print("</form>")

print("</body>")
print("</html>")
