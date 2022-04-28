FROM ubi8/go-toolset:1.16.12-10

ENV NAME=golang \
    GO_MAJOR_VERSION=1 \
    GO_MINOR_VERSION=16 \
    GO_PATCH_VERSION=12 \
    CONTAINER_NAME="rhel8/go-custom" \
    BUILD_DIR="."

# Define the VERSION environment variable in a separate step, so we can
# re-use the GO_MAJOR_VERSION, GO_MINOR_VERSION and GO_PATCH_VERSION variables. 
ENV VERSION=$GO_MAJOR_VERSION.$GO_MINOR_VERSION.$GO_PATCH_VERSION \
    SUMMARY="Platform for building and running Go Applications" \
    DESCRIPTION="Go Toolset available as a container is a base platform for \
building and running various Go applications and frameworks. \
Go is an easy to learn, powerful, statically typed language in the C/C++ \
tradition with garbage collection, concurrent programming support, and memory safety features."

LABEL summary="$SUMMARY" \
      description="$DESCRIPTION" \
      io.k8s.description="$DESCRIPTION" \
      io.k8s.display-name="Go $VERSION" \
      io.openshift.tags="builder,golang,golang${GO_MAJOR_VERSION}${GO_MINOR_VERSION},rh-golang${GO_MAJOR_VERSION}${GO_MINOR_VERSION},go" \
      name="$CONTAINER_NAME" \
      version="$VERSION"

# Copy the S2I scripts from the specific language image to $STI_SCRIPTS_PATH.
COPY ./s2i/bin/ $STI_SCRIPTS_PATH

COPY ./root/ /

RUN chown -R 1001:0 $STI_SCRIPTS_PATH && chown -R 1001:0 $APP_ROOT

USER 1001

# Set the default CMD to print the usage of the language image.
CMD $STI_SCRIPTS_PATH/usage