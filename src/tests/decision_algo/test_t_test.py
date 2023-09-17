from controller.decision import t_test


def test_t_test_positive(hypothesis_mean):
    """Test rejection if sample mean is GREATER than hypothesis mean"""
    sample_size = 100
    sample_mean = 2 * hypothesis_mean
    sample_std = 2
    p_critical = 0.05

    result = t_test(hypothesis_mean, sample_size, sample_mean, sample_std, p_critical)
    assert result


def test_t_test_negative(hypothesis_mean):
    """Test rejection if sample mean is LESS than hypothesis mean"""
    sample_size = 100
    sample_mean = -hypothesis_mean
    sample_std = 2
    p_critical = 0.05

    result = t_test(hypothesis_mean, sample_size, sample_mean, sample_std, p_critical)
    assert result


def test_t_test_no_rejection(hypothesis_mean):
    """Test rejection if sample mean is EQUAL to hypothesis mean"""
    sample_size = 100
    sample_mean = hypothesis_mean
    sample_std = 2
    p_critical = 0.05

    result = t_test(hypothesis_mean, sample_size, sample_mean, sample_std, p_critical)
    assert not result
