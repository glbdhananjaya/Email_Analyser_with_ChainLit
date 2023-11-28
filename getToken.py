from msal import ConfidentialClientApplication

client_id = '9337e364-3c78-444a-be21-24809866b45d'
tenant_id = 'd5e769b0-fd19-45e4-a4a8-b73545450234'
client_secret = 'wbE8Q~nyYTqOoUl06u0L.E5_WgJUTGEOQ~2v0avr'
redirect_uri = 'http://localhost:8000/auth/oauth/azure-ad/callback'
authorization_code = '0.ASoAsGnn1Rn95EWkqLc1RUUCNGTjN5N4PEpEviEkgJhmtF0qAK4.AgABAAIAAAAmoFfGtYxvRrNriQdPKIZ-AgDs_wUA9P-YZ6nkoZQ9lNbwgEHG3O2-vyydz4ly1ZFxowGyK3osKuqGOzWzJFJiUQXxEe4OIIKc9ICLGUF0ObbexCv758CjS6T8xYQ0xo08y5gKsEIBgpldIPCNRcGY3Z7yzZ9BH3oCVCKL04hSdFfERcjT-Y9rrLg2rLQB8MLJxAMkDNxIqQieCYu4aHbNeZ0SRibSQ-KaxSY7bSNTgEcLMbPXRFVINsp-yuRK_9muTy3PF20VvD9MehpvOBX3QGMu8GETveWFoxPQmQJW_czhhDXglmtaayvK8hs5IA9ecWyfGgSAzeaCY6mSJTWrKR-4_9f93EqN7LpAmCb9diFsvC7wOe7vI6p53huEJgwq8_a1MXfIlnCvQ81Hw0QO8optGWFK3GLnhIqJpZgoFjjlU8rnS5eSlbM9RaiVsnswFr9R66x0llW9x8Nl56oBdWfOG8-hfMFURURn1hYQufshOYp0UJSl5j9ke9qKbAFEjuvHiwFZcD6CWZLagtk_i4m9InbwVYrRz8MEJEbQ1YocsNMblMwBe_cnqMHsYz5EXvF_AGDX77IQDXq2AFvp8_XNVzGy9URifJkHSlaecO6_0rrJY3oJQPi2BW0RWRs6Ox14gqTNV9lex_uaN1UE9S5mqvx67Uu2q8_gVRid2plUA5Evqzb_y8zWXvUCeDztPo4czlA2ZQRVHwk_ezpMEy19g745OMr7Bse-18NOK4B0AL7ITajqfke4CnwArDjGF21gaUhSbWyE3_XwLTIZgPs66cidhqkmM-yWwMm7RS_6'
scopes = ['https://graph.microsoft.com/User.Read']

app = ConfidentialClientApplication(
    client_id=client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}",
    client_credential=client_secret,
)

token_response = app.acquire_token_by_authorization_code(
    authorization_code,
    scopes=scopes,
    redirect_uri=redirect_uri,
)

if 'error' in token_response:
    print(f"Error: {token_response['error']}\nDescription: {token_response['error_description']}")
else:
    access_token = token_response['access_token']
    print(f"Access Token:\n{access_token}")
