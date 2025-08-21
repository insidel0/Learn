from learn.srs import review


def test_srs_progression():
    st, _ = review(None, 4)
    assert st.interval == 1
    st2, _ = review(st, 4)
    assert st2.interval == 6
