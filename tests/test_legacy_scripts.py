from pathlib import Path

import pandas as pd


def sample_frame():
    return pd.DataFrame(
        {
            "data": pd.to_datetime(["2026-10-19", "2026-10-20"]),
            "cotacao_dolar": [5.25, 5.3],
        }
    )


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return [
            {"data": "19/10/2026", "valor": "5.2500"},
            {"data": "20/10/2026", "valor": "5.3000"},
        ]


def test_coletar_cotacao_returns_canonical_frame(monkeypatch):
    import coleta

    monkeypatch.setattr(coleta.requests, "get", lambda *args, **kwargs: FakeResponse())

    result = coleta.coletar_cotacao(dias=90)

    assert result.columns.tolist() == ["data", "cotacao_dolar"]
    assert result["cotacao_dolar"].tolist() == [5.25, 5.3]


def test_coleta_main_creates_data_directory_and_csv(tmp_path, monkeypatch):
    import coleta

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(coleta, "coletar_cotacao", lambda dias=90: sample_frame())

    coleta.main()

    files = list((tmp_path / "data").glob("cotacao_dolar_*.csv"))
    assert len(files) == 1
    saved = pd.read_csv(files[0])
    assert saved.columns.tolist() == ["data", "cotacao_dolar"]


def test_carregar_ultimo_csv_selects_latest_filename(tmp_path, monkeypatch):
    import analise

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    sample_frame().assign(cotacao_dolar=[5.0, 5.1]).to_csv(
        data_dir / "cotacao_dolar_2026-10-19.csv", index=False
    )
    sample_frame().to_csv(data_dir / "cotacao_dolar_2026-10-20.csv", index=False)
    monkeypatch.chdir(tmp_path)

    result = analise.carregar_ultimo_csv()

    assert result["cotacao_dolar"].tolist() == [5.25, 5.3]


def test_gerar_grafico_creates_images_directory(tmp_path, monkeypatch):
    import analise

    monkeypatch.chdir(tmp_path)

    analise.gerar_grafico(sample_frame())

    assert (tmp_path / "images" / "cotacao_dolar.png").is_file()


def test_analise_main_preserves_summary_output(monkeypatch, capsys):
    import analise

    monkeypatch.setattr(analise, "carregar_ultimo_csv", sample_frame)
    monkeypatch.setattr(analise, "gerar_grafico", lambda frame: None)

    analise.main()

    output = capsys.readouterr().out
    assert "Período: 19/10/2026 a 20/10/2026" in output
    assert "Cotação mínima: R$ 5.2500" in output
    assert "Cotação máxima: R$ 5.3000" in output
    assert "Cotação média:  R$ 5.2750" in output
    assert "Gráfico salvo em images/cotacao_dolar.png" in output
