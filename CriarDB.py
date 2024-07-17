import argparse
from collections import namedtuple
from canlib import kvadblib

Message = namedtuple('Message', 'name id dlc signals')
Signal = namedtuple('Signal', 'name size scaling limits unit')

# Definição da mensagem e do sinal conforme as especificações fornecidas
_messages = [
    Message(
        name='Aftertreatment1OutletGas1',
        id=0x18F00F52,
        dlc=8,
        signals=[
            Signal(
                name='Aftertreatment1OutletNOx',
                size=(0, 16),  # 2 bytes starting at bit 1 (0-based index)
                scaling=(0.05, -200),
                limits=(-200, 3012.75),
                unit="ppm",
            ),
        ],
    ),
]

def create_database(name, filename):
    db = kvadblib.Dbc(name=name)

    for _msg in _messages:
        message = db.new_message(
            name=_msg.name,
            id=_msg.id,
            dlc=_msg.dlc,
        )

        for _sig in _msg.signals:
            message.new_signal(
                name=_sig.name,
                type=kvadblib.SignalType.UNSIGNED,
                byte_order=kvadblib.SignalByteOrder.INTEL,
                mode=kvadblib.SignalMultiplexMode.MUX_INDEPENDENT,
                size=kvadblib.ValueSize(*_sig.size),
                scaling=kvadblib.ValueScaling(*_sig.scaling),
                limits=kvadblib.ValueLimits(*_sig.limits),
                unit=_sig.unit,
            )

    db.write_file(filename)
    db.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a database from scratch.")
    parser.add_argument('filename', help=("The filename to save the database to."))
    parser.add_argument(
        '-n',
        '--name',
        default='AftertreatmentExample',
        help=("The name of the database (not the filename, the internal name)."),
    )
    args = parser.parse_args()

    create_database(args.name, args.filename)
