"""Regression: FilterPipeline had no 'applied_filters' attribute.

The Clean tab stats label (clean_filters.update_filter_stats) reads
pipeline.applied_filters, but FilterPipeline never defined it — loading any
text crashed the tab refresh with AttributeError. The field now lives on
FilterPipeline and is recorded by TextAnalyzerState._apply_filters, the
single place where filtering happens.
"""
from tools.text_tool.ui.state import TextAnalyzerState


def _state_with(text: str) -> TextAnalyzerState:
    state = TextAnalyzerState()
    state.add_text_source(text)
    return state


def test_stopwords_recorded_by_default():
    state = _state_with("la casa de la montaña")
    assert state.filter_pipeline.applied_filters == ["stopwords"]
    # "la" / "de" are stopwords and must not survive filtering
    assert "la" not in state.filter_pipeline.filtered_words
    assert "de" not in state.filter_pipeline.filtered_words


def test_no_filters_when_stopwords_disabled():
    state = _state_with("la casa")
    state.apply_stopwords_filter(False)
    assert state.filter_pipeline.applied_filters == []
    assert "la" in state.filter_pipeline.filtered_words


def test_exclusions_only():
    state = _state_with("casa perro gato")
    state.apply_stopwords_filter(False)
    state.set_exclusions("perro")
    assert state.filter_pipeline.applied_filters == ["exclusiones"]
    assert "perro" not in state.filter_pipeline.filtered_words
    assert "casa" in state.filter_pipeline.filtered_words


def test_both_filters_listed_in_order():
    state = _state_with("la casa perro")
    state.set_exclusions("perro")  # re-filters with default stopwords enabled
    assert state.filter_pipeline.applied_filters == ["stopwords", "exclusiones"]


def test_stats_label_expression_does_not_crash():
    """Mirror of the exact expression used by update_filter_stats."""
    state = _state_with("texto de prueba")
    pipeline = state.filter_pipeline
    filters_text = (
        ", ".join(pipeline.applied_filters) if pipeline.applied_filters else "ninguno"
    )
    assert filters_text == "stopwords"
