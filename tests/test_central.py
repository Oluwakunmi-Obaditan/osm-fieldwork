# Copyright (c) 2022, 2023 Humanitarian OpenStreetMap Team
#
# This file is part of osm_fieldwork.
#
#     Underpass is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Underpass is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with osm_fieldwork.  If not, see <https:#www.gnu.org/licenses/>.
#
"""Test functionalty of OdkCentral.py."""

from io import BytesIO
from pathlib import Path

import segno

testdata_dir = Path(__file__).parent / "testdata"


def test_delete_appuser(appuser, appuser_details, project_details):
    """Create a QR Code for an appuser."""
    response = appuser.delete(
        project_details.get("id"),
        appuser_details.get("id"),
    )
    assert response.ok
    assert response.json().get("success") == True


# def test_update_role(appuser, project_details, appuser_details, xform_details):
#     """Test updating appuser role."""
#     response = appuser.updateRole(
#         projectId=project_details.get("id"), xform=xform_details.get("id"), actorId=appuser_details.get("id")
#     )
#     assert response.ok


# def test_grant_access(appuser, project_details, appuser_details, xform_details):
#     """Create granting appuser access to a form."""
#     response = appuser.grantAccess(
#         projectId=project_details.get("id"), xform=xform_details.get("id"), actorId=appuser_details.get("id")
#     )
#     assert response.ok


def test_create_qrcode(appuser, appuser_details):
    """Create a QR Code for an appuser."""
    qrcode = appuser.createQRCode(
        odk_id=1,
        project_name="test project",
        appuser_token=appuser_details.get("token"),
        basemap="osm",
        osm_username="svchotosm",
        # save_qrcode = False,
    )
    assert isinstance(qrcode, segno.QRCode)

    qrcode = appuser.createQRCode(
        odk_id=1,
        project_name="test project",
        appuser_token=appuser_details.get("token"),
        basemap="osm",
        osm_username="svchotosm",
        save_qrcode=True,
    )
    qrcode_file = Path("test project.png")
    assert qrcode_file.exists()


def test_create_form_delete(project, odk_form):
    """Create form and delete."""
    odk_id, xform = odk_form
    test_xform = testdata_dir / "buildings.xml"

    form_name = xform.createForm(odk_id, str(test_xform))
    assert form_name == "test_form"

    assert len(project.listForms(odk_id)) == 1

    success = xform.deleteForm(odk_id, form_name)
    assert success

    assert len(project.listForms(odk_id)) == 0


def test_create_form_and_publish(project, odk_form):
    """Create form and publish."""
    odk_id, xform = odk_form
    test_xform = testdata_dir / "buildings.xml"

    form_name = xform.createForm(odk_id, str(test_xform))
    assert form_name == "test_form"

    response_code = xform.publishForm(odk_id, form_name)
    assert response_code == 200
    assert xform.published == True

    success = xform.deleteForm(odk_id, form_name)
    assert success

    forms = project.listForms(odk_id)
    assert len(forms) == 0


def test_create_form_and_publish_immediately(project, odk_form):
    """Create form and publish immediately."""
    odk_id, xform = odk_form
    test_xform = testdata_dir / "buildings.xml"

    form_name = xform.createForm(odk_id, str(test_xform), publish=True)
    assert form_name == "test_form"
    assert xform.published == True

    success = xform.deleteForm(odk_id, form_name)
    assert success

    assert len(project.listForms(odk_id)) == 0


def test_create_form_draft(project, odk_form):
    """Create form draft from existing form."""
    odk_id, xform = odk_form
    test_xform = testdata_dir / "buildings.xml"

    # Create original form
    original_form_name = xform.createForm(odk_id, str(test_xform))
    assert original_form_name == "test_form"
    assert xform.draft == False

    # Publish original form
    response_code = xform.publishForm(odk_id, original_form_name)
    assert response_code == 200
    assert xform.published == True

    # Create draft from original form (sleep 1s first for version increment)
    draft_form_name = xform.createForm(odk_id, str(test_xform), original_form_name)
    assert draft_form_name == original_form_name
    assert xform.draft == True

    # Delete the newly created draft
    success = xform.deleteForm(odk_id, draft_form_name)
    assert success

    # Create another draft from original form
    draft_form_name = xform.createForm(odk_id, str(test_xform), original_form_name)
    assert draft_form_name == original_form_name
    assert xform.draft == True

    # Publish newly created version of form
    response_code = xform.publishForm(odk_id, draft_form_name)
    assert response_code == 200
    assert xform.published == True
    assert xform.draft == False

    assert len(project.listForms(odk_id)) == 1

    # Delete published draft form
    success = xform.deleteForm(odk_id, draft_form_name)
    assert success

    assert len(project.listForms(odk_id)) == 0


def test_upload_media_filepath(project, odk_form):
    """Create form and upload media."""
    odk_id, xform = odk_form
    test_xform = testdata_dir / "buildings.xml"

    # Create form
    form_name = xform.createForm(odk_id, str(test_xform))
    assert form_name == "test_form"

    # Publish form first
    response_code = xform.publishForm(odk_id, form_name)
    assert response_code == 200
    assert xform.published == True

    # Upload media
    result = xform.uploadMedia(
        odk_id,
        "test_form",
        str(testdata_dir / "osm_buildings.geojson"),
    )
    assert result.status_code == 200

    # Delete form
    success = xform.deleteForm(odk_id, "test_form")
    assert success

    assert len(project.listForms(odk_id)) == 0


def test_upload_media_bytesio_publish(project, odk_form):
    """Create form and upload media."""
    odk_id, xform = odk_form
    test_xform = testdata_dir / "buildings.xml"
    with open(test_xform, "rb") as xform_file:
        xform_bytesio = BytesIO(xform_file.read())

    # Create form
    form_name = xform.createForm(odk_id, xform_bytesio)
    assert form_name == "test_form"

    # Publish form first
    response_code = xform.publishForm(odk_id, form_name)
    assert response_code == 200
    assert xform.published == True

    # Upload media
    with open(testdata_dir / "osm_buildings.geojson", "rb") as geojson:
        geojson_bytesio = BytesIO(geojson.read())
    result = xform.uploadMedia(odk_id, "test_form", geojson_bytesio, filename="osm_buildings.geojson")
    assert result.status_code == 200

    # Delete form
    success = xform.deleteForm(odk_id, "test_form")
    assert success

    assert len(project.listForms(odk_id)) == 0
