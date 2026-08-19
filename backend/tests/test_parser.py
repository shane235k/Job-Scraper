import pytest
from app.sources.python_org import PythonOrgAdapter
from app.sources.muse import MuseAdapter
from app.engine.parser import PayloadParser

def test_python_org_parser_success():
    adapter = PythonOrgAdapter()
    sample_html = """
    <html>
      <body>
        <ol class="list-recent-jobs">
          <li>
            <span class="listing-company-name">
              <a href="/jobs/9999/">Senior Python Developer</a>
              <br/>
              Acme Corp
            </span>
            <span class="listing-location">Remote, US</span>
            <span class="listing-job-type">Back end</span>
            <time datetime="2026-08-19T12:00:00Z">August 19, 2026</time>
          </li>
        </ol>
      </body>
    </html>
    """
    records = PayloadParser.parse_and_validate(adapter, sample_html, "https://www.python.org/jobs/")
    assert len(records) == 1
    assert records[0]["title"] == "Senior Python Developer"
    assert records[0]["company"] == "Acme Corp"
    assert records[0]["location"] == "Remote, US"
    assert records[0]["source_job_id"] == "9999"

def test_python_org_parser_validation_failure():
    adapter = PythonOrgAdapter()
    broken_html = "<html><body><div>Site Maintenance - No jobs</div></body></html>"
    with pytest.raises(ValueError) as exc_info:
        PayloadParser.parse_and_validate(adapter, broken_html, "https://www.python.org/jobs/")
    assert "PARSER VALIDATION FAILURE" in str(exc_info.value)

def test_muse_parser_success():
    adapter = MuseAdapter()
    sample_json = """
    {
      "results": [
        {
          "id": 12345,
          "name": "Full Stack Engineer",
          "company": {"name": "Tech Corp"},
          "locations": [{"name": "New York, NY"}],
          "refs": {"landing_page": "https://themuse.com/job/12345"},
          "publication_date": "2026-08-19T10:00:00Z"
        }
      ]
    }
    """
    records = PayloadParser.parse_and_validate(adapter, sample_json, "https://www.themuse.com/api/public/jobs")
    assert len(records) == 1
    assert records[0]["title"] == "Full Stack Engineer"
    assert records[0]["company"] == "Tech Corp"
    assert records[0]["source_job_id"] == "12345"

def test_muse_parser_validation_failure():
    adapter = MuseAdapter()
    invalid_json = '{"error": "Invalid API Key"}'
    with pytest.raises(ValueError) as exc_info:
        PayloadParser.parse_and_validate(adapter, invalid_json, "https://www.themuse.com/api/public/jobs")
    assert "PARSER VALIDATION FAILURE" in str(exc_info.value)
