import sys

#sys.path.insert(0, '/home/ubuntu/miniconda3/envs/thesis-env/lib/python3.5/site-packages')
sys.path.insert(0, '/home/ubuntu/miniconda3/envs/thesis-env/lib/python3.6/site-packages')

def application(env, start_response):


    print("Foobar")
    print("executable:", sys.executable)
    print("prefix:", sys.prefix)
    print(sys.version)
    #help('modules')


    import estnltk.vabamorf as vabamorf
    #import vabamorf

    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"]
