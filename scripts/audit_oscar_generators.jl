using Dates

function find_generators(rosetta_root::String)
    generators = String[]
    for (dirpath, _, filenames) in walkdir(rosetta_root)
        if "generate.jl" in filenames
            push!(generators, joinpath(dirpath, "generate.jl"))
        end
    end
    sort!(generators)
    return generators
end

function clean_message(text::AbstractString)
    message = replace(text, r"\s+" => " ")
    return message[1:min(lastindex(message), 500)]
end

function run_generator(generate_path::String, output_root::String)
    sysdir = dirname(generate_path)
    example_dir = normpath(joinpath(sysdir, "..", ".."))
    example_rel = relpath(example_dir, ARGS[1])
    target_dir = joinpath(output_root, example_rel)
    mkpath(target_dir)

    data_path = joinpath(sysdir, "data.mrdi")
    isfile(data_path) && rm(data_path)

    stdout_path = joinpath(target_dir, "stdout.log")
    stderr_path = joinpath(target_dir, "stderr.log")

    success = false
    error_message = ""

    open(stdout_path, "w") do stdout_io
        open(stderr_path, "w") do stderr_io
            redirect_stdout(stdout_io) do
                redirect_stderr(stderr_io) do
                    old = pwd()
                    try
                        cd(sysdir)
                        mod = Module(gensym(:ExampleAudit))
                        Base.include(mod, generate_path)
                        success = isfile(data_path)
                        if !success
                            error_message = "NO_DATA"
                        end
                    catch err
                        error_message = sprint(showerror, err, catch_backtrace())
                    finally
                        cd(old)
                    end
                end
            end
        end
    end

    if success
        cp(data_path, joinpath(target_dir, "data.mrdi"); force = true)
        rm(data_path)
        return (example_rel, true, "")
    end

    isfile(data_path) && rm(data_path)
    return (example_rel, false, clean_message(error_message))
end

function main()
    if length(ARGS) != 3
        error("usage: julia audit_oscar_generators.jl <rosetta-root> <output-root> <profile-id>")
    end

    rosetta_root = abspath(ARGS[1])
    output_root = abspath(ARGS[2])
    profile_id = ARGS[3]
    profile_dir = joinpath(output_root, profile_id)
    mkpath(profile_dir)

    successes = String[]
    failures = Pair{String, String}[]

    for generate_path in find_generators(rosetta_root)
        example_rel, ok, message = run_generator(generate_path, profile_dir)
        if ok
            push!(successes, example_rel)
        else
            push!(failures, example_rel => message)
        end
    end

    open(joinpath(profile_dir, "successes.txt"), "w") do io
        for rel in successes
            println(io, rel)
        end
    end

    open(joinpath(profile_dir, "failures.txt"), "w") do io
        for (rel, message) in failures
            println(io, rel, '\t', message)
        end
    end

    println(profile_id, " successes: ", length(successes))
    println(profile_id, " failures: ", length(failures))
    println("Completed at ", now())
end

main()
