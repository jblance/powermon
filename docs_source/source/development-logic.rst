***************
Powermon Logic
***************


.. mermaid::
    :zoom:
    :config: {"theme": "base", "themeVariables": {"lineColor": "#FFFFFF", "secondaryColor": "#006100"}}

    classDiagram
        direction LR
        Device "1" --o "1" Port 
        Device "1" --o "1" MqttBroker
        Device "1" --o "*" Command
        class Device{
            name
            device_id
            model
            manufacturer
            commands: list[Command]
            port: Port
            mqtt_broker: MqttBroker
            add_command(Command)
            run()
        }
        class Port{
            protocol: Protocol
            run_command(Command)
            send_and_receive(Command) "called from run_command"
        }
        class Protocol{
            protocol_id: str
            command_definitions: dict[int, CommandDefinition]
            add_command_definitions(command_definitions_config, result_type)
            get_command_definition(command: str) -> CommandDefinition
            get_full_command(command: str) -> bytes
        }
        Port "1" --o "1" Protocol
        class Command{
            code: str
            type: str
            override: dict
            outputs: list[Output]
            trigger: Trigger
            command_definition: CommandDefinition
            is_due() -> bool
            build_result(raw_response: bytes, protocol: Protocol) -> Result
        }
        Command "1" --o "*" Output
        Command "1" --o "1" Trigger
        Command "1" --o "1" CommandDefinition
        Command "1" --o "1" Result
        class CommandDefinition{
            code
            description
            help_text: str
            result_type: ResultType
            reading_definitions: list[ReadingDefinition]
            test_responses: list
            regex: str
            get_reading_definition(lookup: str|int) -> ReadingDefinition
        }
        CommandDefinition"1" --o "*" ReadingDefinition
        class ReadingDefinition{
            index
            response_type: ResponseType
            description: str
            device_class: str
            state_class: str
            icon: str
            unit: str
            options: list | dict
            default: int | str
            format_template: str
            reading_from_raw_response(raw_value) -> list[Reading]
            translate_raw_response(raw_value) "calls reading_from_raw_response"
        }
        class Result{
            result_type: ResultType
            command_definition: CommandDefinition
            raw_response: bytes
            readings: list[Reading]
            decode_responses(self, responses) -> list[Reading]
            readings_from_response(response, reading_definition: ReadingDefinition) -> list[Reading]
        }
        class Output{
            name: str
            process(Command, Result, mqtt_broker, device_info)
            multiple_from_config() -> list[Output]
        }

Notes: