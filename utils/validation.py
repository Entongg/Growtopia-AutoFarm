class FarmConfigValidator:

    @staticmethod
    def validate(punch_config, put_config, cycles):

        errors = []

        # Validasi Auto Punch
        try:
            x = int(punch_config["x"])
            y = int(punch_config["y"])
            interval = float(punch_config["interval"])
            max_duration = float(
                punch_config["max_duration"]
            )
            max_actions = int(
                punch_config["max_actions"]
            )

            if x < 0 or y < 0:
                errors.append(
                    "Koordinat Auto Punch tidak boleh negatif."
                )

            if interval < 0:
                errors.append(
                    "Interval Auto Punch tidak valid."
                )

            if max_duration <= 0:
                errors.append(
                    "Durasi Auto Punch harus lebih dari 0."
                )

            if max_actions <= 0:
                errors.append(
                    "Jumlah aksi Auto Punch harus lebih dari 0."
                )

        except (KeyError, TypeError, ValueError):
            errors.append(
                "Konfigurasi Auto Punch tidak valid."
            )

        # Validasi Auto Put
        try:
            positions = put_config["positions"]
            interval = float(put_config["interval"])
            max_duration = float(
                put_config["max_duration"]
            )
            max_actions = int(
                put_config["max_actions"]
            )

            if not positions:
                errors.append(
                    "Posisi Auto Put belum diatur."
                )

            for position in positions:
                if len(position) != 2:
                    errors.append(
                        "Format posisi Auto Put harus (x, y)."
                    )
                    break

                x, y = int(position[0]), int(position[1])

                if x < 0 or y < 0:
                    errors.append(
                        "Koordinat Auto Put tidak boleh negatif."
                    )
                    break

            if interval < 0:
                errors.append(
                    "Interval Auto Put tidak valid."
                )

            if max_duration <= 0:
                errors.append(
                    "Durasi Auto Put harus lebih dari 0."
                )

            if max_actions <= 0:
                errors.append(
                    "Jumlah aksi Auto Put harus lebih dari 0."
                )

        except (KeyError, TypeError, ValueError):
            errors.append(
                "Konfigurasi Auto Put tidak valid."
            )

        # Validasi siklus
        try:
            cycles = int(cycles)

            if cycles <= 0:
                errors.append(
                    "Jumlah siklus harus lebih dari 0."
                )

        except (TypeError, ValueError):
            errors.append(
                "Jumlah siklus tidak valid."
            )

        return errors