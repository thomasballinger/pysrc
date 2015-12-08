example uses:

    vim $(pysrc inspect)

    vimdiff $(pysrc ast.literal_eval -p python2 -p python3)

To use tab completion, add

    complete -C 'pysrc --get-bash-completion' pysrc

For a command that opens the files immediately, try

    complete -C 'pysrc --get-bash-completion' editpy
    function editpy (){
        vim -O $(pysrc "$@")
    }
